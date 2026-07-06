#MenuTitle: Copy Kerning Groups to Font, Keep Values
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__ = """
Rewrite a target font's kerning to use the kerning groups from a source font,
while preserving the target font's kerning values.

Example: if the target has values on @MMK_R_c, but the source font groups the
same glyphs under @MMK_R_o, the target pair is rewritten to @MMK_R_o with the
same numeric value.
"""

from collections import Counter

from GlyphsApp import Glyphs, Message
from vanilla import Button, PopUpButton, TextBox, Window


class KerningGroupConverter(object):

	def __init__(self):
		self.fonts = list(Glyphs.fonts)
		if len(self.fonts) < 2:
			Message(
				title="Copy Kerning Groups",
				message="Open at least two fonts: one source for groups, one target for values.",
			)
			return

		self.font_names = self.unique_font_labels()
		current_index = self.index_for_font(Glyphs.font)
		target_index = 0 if current_index != 0 else 1

		self.w = Window((430, 178), "Copy Kerning Groups")
		self.w.sourceLabel = TextBox((15, 18, 135, 22), "Use groups from")
		self.w.source = PopUpButton((150, 14, 265, 24), self.font_names)
		self.w.source.set(current_index)

		self.w.targetLabel = TextBox((15, 52, 135, 22), "Keep values in")
		self.w.target = PopUpButton((150, 48, 265, 24), self.font_names)
		self.w.target.set(target_index)

		self.w.note = TextBox(
			(15, 86, 400, 42),
			"The target font's glyph kerning groups and kerning pair keys will be rewritten to match the source font. Kerning values come from the target font.",
			sizeStyle="small",
		)
		self.w.convertButton = Button((285, 138, 130, 24), "Convert", callback=self.convert_callback)
		self.w.setDefaultButton(self.w.convertButton)
		self.w.open()
		self.w.makeKey()

	def unique_font_labels(self):
		raw_labels = [self.font_label(font) for font in self.fonts]
		counts = Counter(raw_labels)
		seen = {}
		labels = []
		for label in raw_labels:
			if counts[label] == 1:
				labels.append(label)
			else:
				seen[label] = seen.get(label, 0) + 1
				labels.append("%s [%i]" % (label, seen[label]))
		return labels

	def font_label(self, font):
		family_name = font.familyName or "Untitled"
		file_path = font.filepath
		if file_path:
			try:
				file_name = file_path.lastPathComponent()
			except Exception:
				file_name = str(file_path).split("/")[-1]
			return "%s (%s)" % (family_name, file_name)
		return family_name

	def index_for_font(self, font):
		for i, open_font in enumerate(self.fonts):
			if open_font == font:
				return i
		return 0

	def convert_callback(self, sender):
		source_font = self.fonts[self.w.source.get()]
		target_font = self.fonts[self.w.target.get()]

		if source_font == target_font:
			Message(title="Copy Kerning Groups", message="Choose two different fonts.")
			return

		Glyphs.clearLog()
		Glyphs.showMacroWindow()

		print("COPY KERNING GROUPS TO FONT, KEEP VALUES\n")
		print("Groups from: %s" % self.font_label(source_font))
		print("Values in:   %s" % self.font_label(target_font))
		print()

		target_font.disableUpdateInterface()
		try:
			result = self.convert_target_to_source_groups(source_font, target_font)
		finally:
			target_font.enableUpdateInterface()

		self.w.close()
		self.report(result)

	def report(self, result):
		print("Done.")
		print("  Glyph groups updated: %i" % result["groups_updated"])
		print("  Kerning pairs written: %i" % result["pairs_written"])
		print("  Kerning pairs skipped: %i" % result["pairs_skipped"])
		print("  Unique target pairs touched: %i" % result["unique_pairs"])

		if result["conflicts"]:
			print("\nConflicts:")
			for message in result["conflicts"][:100]:
				print("  %s" % message)
			if len(result["conflicts"]) > 100:
				print("  ... %i more" % (len(result["conflicts"]) - 100))

		if result["warnings"]:
			warnings = sorted(set(result["warnings"]))
			print("\nWarnings:")
			for message in warnings[:100]:
				print("  %s" % message)
			if len(warnings) > 100:
				print("  ... %i more" % (len(warnings) - 100))

		message = "Updated %i glyph group assignments and wrote %i kerning pairs." % (
			result["groups_updated"],
			result["pairs_written"],
		)
		if result["pairs_skipped"]:
			message += "\n\nSkipped %i pair(s). See Macro Window for details." % result["pairs_skipped"]
		Message(title="Copy Kerning Groups", message=message)

	def convert_target_to_source_groups(self, source_font, target_font):
		warnings = []
		conflicts = []
		translated_by_master = {}
		pairs_written = 0
		pairs_skipped = 0

		for target_master in target_font.masters:
			target_kerning = target_font.kerning.get(target_master.id, {})
			translated_pairs = {}

			for target_left, target_rights in target_kerning.items():
				new_left_keys = self.translate_pair_key(target_font, source_font, target_left, "left", warnings)
				if not new_left_keys:
					pairs_skipped += len(target_rights)
					continue

				for target_right, value in target_rights.items():
					new_right_keys = self.translate_pair_key(target_font, source_font, target_right, "right", warnings)
					if not new_right_keys:
						pairs_skipped += 1
						continue

					for new_left in new_left_keys:
						for new_right in new_right_keys:
							pair_key = (new_left, new_right)
							if pair_key in translated_pairs and translated_pairs[pair_key] != value:
								conflicts.append(
									"%s: %s %s has multiple target values (%s, %s); kept first"
									% (target_master.name, new_left, new_right, translated_pairs[pair_key], value)
								)
								pairs_skipped += 1
								continue

							translated_pairs[pair_key] = value

			translated_by_master[target_master.id] = translated_pairs

		groups_updated = self.copy_group_assignments(source_font, target_font, warnings)
		self.clear_target_kerning(target_font)

		for target_master in target_font.masters:
			for pair_key, value in translated_by_master.get(target_master.id, {}).items():
				left_key, right_key = pair_key
				target_font.setKerningForPair(target_master.id, left_key, right_key, value)
				pairs_written += 1

		return {
			"groups_updated": groups_updated,
			"pairs_written": pairs_written,
			"pairs_skipped": pairs_skipped,
			"unique_pairs": sum(len(pairs) for pairs in translated_by_master.values()),
			"warnings": warnings,
			"conflicts": conflicts,
		}

	def clear_target_kerning(self, font):
		for master in font.masters:
			font.kerning[master.id] = {}

	def copy_group_assignments(self, source_font, target_font, warnings):
		changed = 0
		for target_glyph in target_font.glyphs:
			source_glyph = source_font.glyphs[target_glyph.name]
			if not source_glyph:
				warnings.append("No source glyph for target /%s; kept its group assignments" % target_glyph.name)
				continue

			if target_glyph.leftKerningGroup != source_glyph.leftKerningGroup:
				target_glyph.leftKerningGroup = source_glyph.leftKerningGroup
				changed += 1

			if target_glyph.rightKerningGroup != source_glyph.rightKerningGroup:
				target_glyph.rightKerningGroup = source_glyph.rightKerningGroup
				changed += 1

		return changed

	def translate_pair_key(self, value_font, group_font, key, side, warnings):
		if key.startswith("@"):
			return self.translate_group_key(value_font, group_font, key, side, warnings)

		value_glyph = self.glyph_for_id(value_font, key)
		if not value_glyph:
			warnings.append("No target glyph found for kerning ID: %s" % key)
			return None

		if not group_font.glyphs[value_glyph.name]:
			warnings.append("No source glyph for target glyph /%s" % value_glyph.name)
			return None

		# setKerningForPair expects glyph names, not the IDs used internally by font.kerning.
		return [value_glyph.name]

	def translate_group_key(self, value_font, group_font, key, side, warnings):
		prefix = self.prefix_for_key(key)
		if not prefix:
			warnings.append("Unsupported kerning group key: %s" % key)
			return None

		group_name = key[7:]
		value_group_attr = self.group_attribute_for_side(side)
		glyph_names = [
			glyph.name
			for glyph in value_font.glyphs
			if getattr(glyph, value_group_attr) == group_name
		]

		if not glyph_names:
			warnings.append("No target glyphs found in group %s" % key)
			return None

		new_keys = []
		for glyph_name in glyph_names:
			source_glyph = group_font.glyphs[glyph_name]
			if source_glyph:
				source_group = getattr(source_glyph, value_group_attr)
				if source_group:
					new_keys.append("%s%s" % (prefix, source_group))
				else:
					new_keys.append(glyph_name)

		if not new_keys:
			warnings.append("No source glyphs found for target group %s" % key)
			return None

		return self.unique_in_order(new_keys)

	def unique_in_order(self, items):
		seen = set()
		result = []
		for item in items:
			if item not in seen:
				result.append(item)
				seen.add(item)
		return result

	def prefix_for_key(self, key):
		if key.startswith("@MMK_L_"):
			return "@MMK_L_"
		if key.startswith("@MMK_R_"):
			return "@MMK_R_"
		return None

	def group_attribute_for_side(self, side):
		if side == "left":
			return "rightKerningGroup"
		return "leftKerningGroup"

	def glyph_for_id(self, font, glyph_id):
		try:
			return font.glyphForId_(glyph_id)
		except Exception:
			return None


KerningGroupConverter()
