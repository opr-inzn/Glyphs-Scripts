#MenuTitle: Adapt Selected Sidebearings to Space Width
# -*- coding: utf-8 -*-
__doc__ = """
For selected glyphs, reads the left/right sidebearing relationship from one
master and applies it to another master. The target layer width is taken from
the target master's space glyph.
"""

from GlyphsApp import Glyphs, Message
from vanilla import Button, PopUpButton, TextBox, Window


class AdaptSelectedSidebearingsToSpaceWidth(object):

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
			"Target width comes from the space glyph in the target master.",
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

		space = self.font.glyphs["space"]
		if space is None:
			Message(title="Adapt Sidebearings", message="The font has no space glyph.")
			return

		space_layer = space.layers[target_master.id]
		target_width = space_layer.width
		if target_width <= 0:
			Message(
				title="Adapt Sidebearings",
				message="The target master's space glyph has no usable width.",
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

				target_bounds = target_layer.bounds
				target_black_width = target_bounds.size.width
				total_target_sb = target_width - target_black_width

				if total_target_sb < 0:
					skipped.append("%s: target outline is wider than space" % glyph.name)
					continue

				left_ratio = source_layer.LSB / float(total_source_sb)
				new_lsb = round(total_target_sb * left_ratio)
				new_rsb = target_width - target_black_width - new_lsb

				glyph.beginUndo()
				try:
					target_layer.width = target_width
					target_layer.LSB = new_lsb
					target_layer.RSB = new_rsb
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


AdaptSelectedSidebearingsToSpaceWidth()
