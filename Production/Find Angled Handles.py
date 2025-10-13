#MenuTitle: Find Angled Handles
# -*- coding: utf-8 -*-

"""
Finds all glyphs that have angled handles (non-horizontal/vertical BCPs)
on smooth nodes with handles on both sides across all masters, marks them with annotations, and opens them in separate tabs per master.
"""

from math import atan2, degrees
from GlyphsApp import Glyphs, Message, GSAnnotation
from AppKit import NSPoint

def angle_of_handle(node, handle):
    """
    Calculate the angle of a BCP handle.
    Returns angle in degrees.
    """
    if handle.type == OFFCURVE:
        dx = handle.x - node.x
        dy = handle.y - node.y
        return degrees(atan2(dy, dx))
    return None

def is_angled_handle(angle, threshold=1.0):
    """
    Check if an angle is not horizontal or vertical.
    threshold: degrees of tolerance (default 1.0°)
    """
    if angle is None:
        return False
    
    # Normalize to 0-360
    angle = angle % 360
    
    # Check if not horizontal (0°, 180°) or vertical (90°, 270°)
    horizontal = abs(angle) < threshold or abs(angle - 180) < threshold or abs(angle - 360) < threshold
    vertical = abs(angle - 90) < threshold or abs(angle - 270) < threshold
    
    return not (horizontal or vertical)

def has_handles_on_both_sides(node):
    """
    Check if a node has handles on both sides.
    """
    has_prev_handle = node.prevNode and node.prevNode.type == OFFCURVE
    has_next_handle = node.nextNode and node.nextNode.type == OFFCURVE
    return has_prev_handle and has_next_handle

def find_and_mark_angled_handles(font, threshold=1.0):
    """
    Find all glyphs that have angled handles on smooth nodes per master and mark them.
    Returns a dictionary: {master_id: set(glyph_names)}
    """
    affected_by_master = {}
    
    # Initialize dictionary with master IDs
    for master in font.masters:
        affected_by_master[master.id] = set()
    
    for glyph in font.glyphs:
        # Check each master separately
        for master in font.masters:
            layer = glyph.layers[master.id]
            has_angled = False
            
            # Check all paths
            for path in layer.paths:
                for i, node in enumerate(path.nodes):
                    # Only check smooth nodes with handles on both sides
                    if node.smooth and has_handles_on_both_sides(node):
                        # Check incoming handle
                        if node.type == CURVE or node.type == QCURVE:
                            if node.prevNode and node.prevNode.type == OFFCURVE:
                                angle = angle_of_handle(node, node.prevNode)
                                if is_angled_handle(angle, threshold):
                                    has_angled = True
                                    # Add annotation at the handle
                                    annotation = GSAnnotation()
                                    annotation.type = TEXT
                                    annotation.text = f"∠ {angle:.1f}°"
                                    annotation.position = NSPoint(
                                        node.prevNode.x,
                                        node.prevNode.y
                                    )
                                    layer.annotations.append(annotation)
                            
                            # Check outgoing handle
                            if node.nextNode and node.nextNode.type == OFFCURVE:
                                angle = angle_of_handle(node, node.nextNode)
                                if is_angled_handle(angle, threshold):
                                    has_angled = True
                                    # Add annotation at the handle
                                    annotation = GSAnnotation()
                                    annotation.type = TEXT
                                    annotation.text = f"∠ {angle:.1f}°"
                                    annotation.position = NSPoint(
                                        node.nextNode.x,
                                        node.nextNode.y
                                    )
                                    layer.annotations.append(annotation)
            
            if has_angled:
                affected_by_master[master.id].add(glyph.name)
    
    return affected_by_master

def clear_angled_handle_annotations(font):
    """
    Clear existing angled handle annotations (those starting with ∠).
    """
    for glyph in font.glyphs:
        for layer in glyph.layers:
            if layer.isMasterLayer or layer.isSpecialLayer:
                annotations_to_remove = []
                for annotation in layer.annotations:
                    if annotation.text and annotation.text.startswith("∠"):
                        annotations_to_remove.append(annotation)
                
                for annotation in annotations_to_remove:
                    layer.annotations.remove(annotation)

# Main execution
font = Glyphs.font

if not font:
    Message("No Font Open", "Please open a font first.", OKButton=None)
else:
    # Clear previous annotations
    print("Clearing previous angled handle annotations...")
    clear_angled_handle_annotations(font)
    
    print("Searching for smooth nodes with angled handles...")
    affected_by_master = find_and_mark_angled_handles(font, threshold=1.0)
    
    total_count = 0
    tabs_opened = 0
    
    # Open separate tab for each master with affected glyphs
    for master in font.masters:
        affected_glyphs = affected_by_master[master.id]
        
        if affected_glyphs:
            sorted_glyphs = sorted(affected_glyphs)
            total_count += len(sorted_glyphs)
            
            print(f"\n{master.name}: {len(sorted_glyphs)} glyphs with angled handles")
            for glyph_name in sorted_glyphs:
                print(f"  - {glyph_name}")
            
            # Create tab with master name at the beginning
            tab_text = f"{master.name}\n/" + "/".join(sorted_glyphs)
            new_tab = font.newTab(tab_text)
            # Set the tab to display the specific master
            new_tab.masterIndex = font.masters.index(master)
            tabs_opened += 1
    
    if total_count > 0:
        Message(
            "Angled Handles Found",
            f"Found {total_count} glyphs with angled handles across {tabs_opened} master(s).\nMarked with annotations and opened in separate tabs.",
            OKButton=None
        )
    else:
        print("\nNo smooth nodes with angled handles found.")
        Message(
            "No Angled Handles",
            "No smooth nodes with angled handles were found in this font.",
            OKButton=None
        )