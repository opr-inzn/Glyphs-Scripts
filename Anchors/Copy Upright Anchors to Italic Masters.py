#MenuTitle: Copy Upright _center Anchors to Italic Masters
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals

__doc__ = """
For selected glyphs, copies each _center anchor from an upright master to its
matching italic master. Masters are matched by every design axis except Italic
or Slant. The copied position is then slanted by the italic master's Italic
Angle around half of that master's x-height.

An existing _center anchor is moved; a missing one is added. All other anchors
are left untouched.
"""

import math

from AppKit import NSPoint
from GlyphsApp import GSAnchor, Glyphs, Message


EPSILON = 0.001
ITALIC_AXIS_TAGS = ("ital", "slnt")
ANCHOR_NAME = "_center"


def selected_glyphs(font):
	glyphs = []
	seen = set()
	for layer in font.selectedLayers:
		glyph = layer.parent
		if glyph is not None and glyph.name not in seen:
			glyphs.append(glyph)
			seen.add(glyph.name)
	return glyphs


def italic_axis_indexes(font):
	indexes = []
	for index, axis in enumerate(font.axes):
		tag = getattr(axis, "axisTag", "") or ""
		name = getattr(axis, "name", "") or ""
		if tag.lower() in ITALIC_AXIS_TAGS or name.lower() in ("italic", "slant"):
			indexes.append(index)
	return indexes


def axis_value(master, index):
	values = list(master.axes)
	return values[index] if index < len(values) else 0.0


def is_italic_master(master, italic_indexes):
	if abs(master.italicAngle) > EPSILON or bool(getattr(master, "isItalic", False)):
		return True
	return any(abs(axis_value(master, index)) > EPSILON for index in italic_indexes)


def matching_coordinates(first_master, second_master, ignored_indexes):
	coordinate_count = max(len(first_master.axes), len(second_master.axes))
	for index in range(coordinate_count):
		if index in ignored_indexes:
			continue
		if abs(axis_value(first_master, index) - axis_value(second_master, index)) > EPSILON:
			return False
	return True


def normalized_style_name(name):
	words = name.lower().replace("-", " ").split()
	return " ".join(word for word in words if word not in ("italic", "oblique", "slanted"))


def upright_for_italic(italic_master, upright_masters, italic_indexes):
	candidates = [
		master
		for master in upright_masters
		if matching_coordinates(master, italic_master, italic_indexes)
	]
	if not candidates:
		return None
	if len(candidates) == 1:
		return candidates[0]

	link_style = getattr(italic_master, "linkStyle", None)
	if link_style:
		for master in candidates:
			if master.name == link_style:
				return master

	normalized_italic_name = normalized_style_name(italic_master.name)
	for master in candidates:
		if normalized_style_name(master.name) == normalized_italic_name:
			return master

	return candidates[0]


def italicized_position(position, italic_master):
	pivot_y = italic_master.xHeight * 0.5
	x_offset = math.tan(math.radians(italic_master.italicAngle)) * (position.y - pivot_y)
	return NSPoint(position.x + x_offset, position.y)


def copy_anchor(glyph, upright_master, italic_master):
	upright_layer = glyph.layers[upright_master.id]
	italic_layer = glyph.layers[italic_master.id]
	if upright_layer is None or italic_layer is None:
		return 0, "%s: missing upright or italic layer" % glyph.name

	upright_anchor = upright_layer.anchorForName_(ANCHOR_NAME)
	if upright_anchor is None:
		return 0, "%s: upright layer has no %s anchor" % (glyph.name, ANCHOR_NAME)

	position = italicized_position(upright_anchor.position, italic_master)
	italic_anchor = italic_layer.anchorForName_(ANCHOR_NAME)
	if italic_anchor is None:
		italic_anchor = GSAnchor(ANCHOR_NAME, position)
		italic_layer.addAnchor_(italic_anchor)
	else:
		italic_anchor.setPosition_(position)

	print(
		"%s, %s -> %s: %s at %.1f, %.1f"
		% (
			glyph.name,
			upright_master.name,
			italic_master.name,
			ANCHOR_NAME,
			position.x,
			position.y,
		)
	)

	return 1, None


font = Glyphs.font
if font is None:
	Message(title="Copy _center to Italics", message="No font open.")
else:
	glyphs = selected_glyphs(font)
	if not glyphs:
		Message(title="Copy _center to Italics", message="No glyphs selected.")
	else:
		italic_indexes = italic_axis_indexes(font)
		upright_masters = [
			master for master in font.masters if not is_italic_master(master, italic_indexes)
		]
		italic_masters = [
			master for master in font.masters if is_italic_master(master, italic_indexes)
		]

		pairs = []
		skipped = []
		for italic_master in italic_masters:
			upright_master = upright_for_italic(
				italic_master,
				upright_masters,
				italic_indexes,
			)
			if upright_master is None:
				skipped.append("%s: no matching upright master" % italic_master.name)
			else:
				pairs.append((upright_master, italic_master))

		if not pairs:
			Message(
				title="Copy _center to Italics",
				message="No matching upright/italic master pairs were found.",
			)
		else:
			changed_count = 0
			font.disableUpdateInterface()
			try:
				for glyph in glyphs:
					glyph.beginUndo()
					try:
						for upright_master, italic_master in pairs:
							changed, error = copy_anchor(
								glyph,
								upright_master,
								italic_master,
							)
							changed_count += changed
							if error is not None:
								skipped.append(
									"%s -> %s, %s"
									% (upright_master.name, italic_master.name, error)
								)
					finally:
						glyph.endUndo()
			finally:
				font.enableUpdateInterface()

			Glyphs.redraw()
			Glyphs.showNotification(
				"Copy _center to Italics",
				"Copied %i _center position(s) across %i master pair(s)."
				% (changed_count, len(pairs)),
			)

			if skipped:
				print("Skipped:")
				for skipped_message in skipped:
					print("  " + skipped_message)
