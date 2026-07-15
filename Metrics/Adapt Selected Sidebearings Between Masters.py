#MenuTitle: Adapt Selected Sidebearings Between Masters
# -*- coding: utf-8 -*-
__doc__ = """
For selected glyphs, reads the relationship between outline width and the
left/right sidebearings from one master and applies it to another master while
keeping the target layer's width unchanged.
"""

from GlyphsApp import Glyphs, Message
from vanilla import Button, PopUpButton, TextBox, Window


class AdaptSelectedSidebearingsBetweenMasters(object):

	def __init__(self):
		self.font = Glyphs.font
		if self.font is None:
			Message(title="Adapt Sidebearings", message="No font open.")
			return

		self.masters = list(self.font.masters)
		if len(self.masters) < 2:
			Message(title="Adapt Sidebearings", message="This script needs at least two masters.")
			return

		current_master_id = self.font.selectedFontMaster.id
		current_index = self.master_index_for_id(current_master_id)
		source_index = 0 if current_index != 0 else min(1, len(self.masters) - 1)

		self.w = Window((360, 142), "Adapt Sidebearings")
		self.w.sourceLabel = TextBox((15, 18, 105, 22), "Read from")
		self.w.source = PopUpButton((120, 14, 225, 24), self.master_names())
		self.w.source.set(source_index)

		self.w.targetLabel = TextBox((15, 52, 105, 22), "Apply to")
		self.w.target = PopUpButton((120, 48, 225, 24), self.master_names())
		self.w.target.set(current_index)

		self.w.note = TextBox(
			(15, 84, 330, 28),
			"The target glyph's existing width is preserved.",
			sizeStyle="small",
		)
		self.w.applyButton = Button((215, 106, 130, 24), "Apply", callback=self.apply_callback)
		self.w.setDefaultButton(self.w.applyButton)
		self.w.open()
		self.w.makeKey()

	def master_names(self):
		return [master.name for master in self.masters]

	def master_index_for_id(self, master_id):
		for i, master in enumerate(self.masters):
			if master.id == master_id:
				return i
		return 0

	def selected_glyphs(self):
		glyphs = []
		seen = set()
		for layer in self.font.selectedLayers:
			glyph = layer.parent
			if glyph and glyph.name not in seen:
				glyphs.append(glyph)
				seen.add(glyph.name)
		return glyphs

	def apply_callback(self, sender):
		source_master = self.masters[self.w.source.get()]
		target_master = self.masters[self.w.target.get()]

		if source_master.id == target_master.id:
			Message(
				title="Adapt Sidebearings",
				message="Choose two different masters.",
			)
			return

		glyphs = self.selected_glyphs()
		if not glyphs:
			Message(title="Adapt Sidebearings", message="No glyphs selected.")
			return

		changed = 0
		skipped = []

		self.font.disableUpdateInterface()
		try:
			for glyph in glyphs:
				source_layer = glyph.layers[source_master.id]
				target_layer = glyph.layers[target_master.id]

				if source_layer is None or target_layer is None:
					skipped.append("%s: missing source or target layer" % glyph.name)
					continue

				total_source_sb = source_layer.LSB + source_layer.RSB
				if total_source_sb == 0:
					skipped.append("%s: source sidebearings add up to zero" % glyph.name)
					continue

				target_width = target_layer.width
				target_bounds = target_layer.bounds
				target_black_width = target_bounds.size.width
				if target_black_width <= 0:
					skipped.append("%s: target layer has no usable outline" % glyph.name)
					continue

				# Divide the space available inside the target's existing width in the
				# same left/right proportion as the source sidebearings.
				total_target_sb = target_width - target_black_width
				left_ratio = source_layer.LSB / float(total_source_sb)
				new_lsb = round(total_target_sb * left_ratio)
				new_rsb = total_target_sb - new_lsb

				glyph.beginUndo()
				try:
					target_layer.LSB = new_lsb
					# Setting sidebearings can affect the advance width. Restore it last
					# so this script can never leave the target at a different width.
					target_layer.width = target_width
				finally:
					glyph.endUndo()

				changed += 1
				print(
					"%s: %s L/R %s/%s -> %s width %s, L/R %s/%s"
					% (
						glyph.name,
						source_master.name,
						source_layer.LSB,
						source_layer.RSB,
						target_master.name,
						target_width,
						new_lsb,
						new_rsb,
					)
				)
		finally:
			self.font.enableUpdateInterface()

		self.w.close()

		message = "Updated %i selected glyph(s)." % changed
		if skipped:
			message += "\n\nSkipped:\n" + "\n".join(skipped[:10])
			if len(skipped) > 10:
				message += "\n...and %i more." % (len(skipped) - 10)

		Message(title="Adapt Sidebearings", message=message)


AdaptSelectedSidebearingsBetweenMasters()
