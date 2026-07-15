#MenuTitle: Sharpen Selected Corner in All Masters
# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals

__doc__ = """
Sharpens one selected outline section in every master of the current glyph.
The layers must be compatible: the corresponding path and node indexes are
used in each master.

Select the rounded corner section in Edit view before running the script.
"""

from Foundation import NSClassFromString
from GlyphsApp import GSNode, Glyphs, Message, OFFCURVE


def selected_path_and_nodes(font):
	matches = []

	for layer in font.selectedLayers:
		selected_nodes = [item for item in layer.selection if isinstance(item, GSNode)]
		if not selected_nodes:
			continue

		paths = []
		for node in selected_nodes:
			path = node.parent
			if path is not None and path not in paths:
				paths.append(path)

		for path in paths:
			path_nodes = [node for node in selected_nodes if node.parent == path]
			matches.append((layer, path, path_nodes))

	if len(matches) != 1:
		return None, None, None, "Select one corner section on one path."

	layer, path, nodes = matches[0]
	if len(nodes) < 2:
		return None, None, None, "Select at least two nodes around the corner."

	return layer, path, nodes, None


def path_index_in_layer(layer, selected_path):
	for index, path in enumerate(layer.paths):
		if path == selected_path:
			return index
	return None


def selected_node_range(path, selected_nodes):
	node_count = len(path.nodes)
	indices = sorted(set(node.index for node in selected_nodes))

	if node_count < 3 or len(indices) < 2:
		return None, None, "The selected path does not contain a corner section."
	if len(indices) == node_count:
		return None, None, "Select only the corner section, not the entire path."

	# The selected nodes form a run on a circular node list. The largest gap is
	# outside that run, so the nodes immediately after and before it are the
	# start and end of the corner. This also handles a selection across node 0.
	largest_gap = -1
	start_index = None
	end_index = None
	for position, index in enumerate(indices):
		next_index = indices[(position + 1) % len(indices)]
		gap = (next_index - index) % node_count
		if gap > largest_gap:
			largest_gap = gap
			start_index = next_index
			end_index = index

	if largest_gap <= 1:
		return None, None, "Could not determine the limits of the selected corner."

	if path.nodes[start_index].type == OFFCURVE or path.nodes[end_index].type == OFFCURVE:
		return None, None, "The corner selection must start and end on on-curve nodes."

	return start_index, end_index, None


def corner_tool(font):
	try:
		controller = font.parent.windowController()
		tool = controller.toolEventHandler() if controller is not None else None
		if tool is not None and hasattr(tool, "_makeCorner_firstNodeIndex_endNodeIndex_"):
			return tool
	except Exception:
		pass

	tool_class = NSClassFromString("GSToolSelect")
	if tool_class is not None:
		tool = tool_class.alloc().init()
		if hasattr(tool, "_makeCorner_firstNodeIndex_endNodeIndex_"):
			return tool

	return None


def master_paths(glyph, path_index, expected_node_count):
	paths = []
	skipped = []
	for master in glyph.parent.masters:
		layer = glyph.layers[master.id]
		if layer is None:
			skipped.append("%s: missing layer" % master.name)
			continue
		if path_index >= len(layer.paths):
			skipped.append("%s: corresponding path is missing" % master.name)
			continue

		path = layer.paths[path_index]
		if len(path.nodes) != expected_node_count:
			skipped.append("%s: corresponding path is not compatible" % master.name)
			continue

		paths.append((master, layer, path))

	return paths, skipped


font = Glyphs.font
if font is None:
	Message(title="Sharpen Corner", message="No font open.")
else:
	selected_layer, selected_path, selected_nodes, error = selected_path_and_nodes(font)
	if error is not None:
		Message(title="Sharpen Corner", message=error)
	else:
		path_index = path_index_in_layer(selected_layer, selected_path)
		start_index, end_index, error = selected_node_range(selected_path, selected_nodes)

		if path_index is None:
			error = "Could not find the selected path in its layer."

		if error is not None:
			Message(title="Sharpen Corner", message=error)
		else:
			glyph = selected_layer.parent
			expected_node_count = len(selected_path.nodes)
			paths, skipped = master_paths(glyph, path_index, expected_node_count)
			tool = corner_tool(font)

			if not paths:
				Message(
					title="Sharpen Corner",
					message="No master has a compatible corresponding path.",
				)
			elif tool is None:
				Message(
					title="Sharpen Corner",
					message="Glyphs' internal Make Corner tool is unavailable.",
				)
			else:
				# Glyphs expects a negative start index when the selected section
				# crosses the path's first node.
				tool_start_index = start_index
				if start_index > end_index:
					tool_start_index -= expected_node_count

				changed_count = 0
				font.disableUpdateInterface()
				glyph.beginUndo()
				try:
					for master, layer, path in paths:
						before_count = len(path.nodes)
						tool._makeCorner_firstNodeIndex_endNodeIndex_(
							path,
							tool_start_index,
							end_index,
						)
						removed_count = before_count - len(path.nodes)
						changed_count += 1
						print(
							"%s, %s: sharpened path %i, removed %i node(s)"
							% (glyph.name, master.name, path_index + 1, removed_count)
						)
				finally:
					glyph.endUndo()
					font.enableUpdateInterface()

				Glyphs.redraw()
				Glyphs.showNotification(
					"Sharpen Corner",
					"Sharpened %i master(s) of %s; skipped %i."
					% (changed_count, glyph.name, len(skipped)),
				)

				if skipped:
					print("Skipped masters:")
					for skipped_message in skipped:
						print("  " + skipped_message)
