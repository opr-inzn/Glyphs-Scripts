# MenuTitle: Find Glyphs Outside Alignment Zones
# -*- coding: utf-8 -*-

"""
Checks if the top and bottom-most nodes in each glyph are aligned
with vertical metrics or alignment zones across all masters.
Marks misaligned nodes with annotations and opens them in separate tabs per master.
"""

from GlyphsApp import Glyphs, Message, GSAnnotation
from AppKit import NSPoint

def get_alignment_zones(master):
    """
    Get all alignment zones for a master.
    Returns a list of tuples: (position, size, name)
    """
    zones = []
    
    # Add alignment zones
    if master.alignmentZones:
        for i, zone in enumerate(master.alignmentZones):
            zones.append((zone.position, zone.size, f"Zone {i+1}"))
    
    return zones

def get_vertical_metrics(master):
    """
    Get vertical metrics for a master.
    Returns a list of tuples: (position, name)
    """
    metrics = []
    
    # Common vertical metrics
    if hasattr(master, 'ascender') and master.ascender is not None:
        metrics.append((master.ascender, "Ascender"))
    if hasattr(master, 'capHeight') and master.capHeight is not None:
        metrics.append((master.capHeight, "Cap Height"))
    if hasattr(master, 'xHeight') and master.xHeight is not None:
        metrics.append((master.xHeight, "x-Height"))
    if hasattr(master, 'descender') and master.descender is not None:
        metrics.append((master.descender, "Descender"))
    
    # Baseline is always at 0
    metrics.append((0, "Baseline"))
    
    return metrics

def is_in_alignment_zone(y_pos, zones, tolerance=1):
    """
    Check if a y position falls within any alignment zone.
    Returns (True, zone_name) or (False, None)
    """
    for position, size, name in zones:
        zone_min = min(position, position + size)
        zone_max = max(position, position + size)
        if zone_min - tolerance <= y_pos <= zone_max + tolerance:
            return True, name
    return False, None

def is_on_vertical_metric(y_pos, metrics, tolerance=1):
    """
    Check if a y position is on a vertical metric.
    Returns (True, metric_name) or (False, None)
    """
    for metric_pos, name in metrics:
        if abs(y_pos - metric_pos) <= tolerance:
            return True, name
    return False, None

def get_extreme_nodes(layer):
    """
    Get the topmost and bottommost nodes in a layer.
    Returns (top_nodes, bottom_nodes) where each is a list of nodes at that extreme.
    """
    if not layer.paths:
        return [], []
    
    all_nodes = []
    for path in layer.paths:
        for node in path.nodes:
            # Only consider on-curve nodes
            if node.type != OFFCURVE:
                all_nodes.append(node)
    
    if not all_nodes:
        return [], []
    
    # Find extreme y values
    max_y = max(node.y for node in all_nodes)
    min_y = min(node.y for node in all_nodes)
    
    # Get all nodes at these extremes (within 1 unit tolerance)
    top_nodes = [node for node in all_nodes if abs(node.y - max_y) <= 1]
    bottom_nodes = [node for node in all_nodes if abs(node.y - min_y) <= 1]
    
    return top_nodes, bottom_nodes

def check_alignment(font, tolerance=1):
    """
    Check alignment of extreme nodes across all masters.
    Returns a dictionary: {master_id: set(glyph_names)}
    """
    affected_by_master = {}
    
    for master in font.masters:
        affected_by_master[master.id] = set()
        
        # Get alignment references for this master
        zones = get_alignment_zones(master)
        metrics = get_vertical_metrics(master)
        
        print(f"\n{master.name}:")
        print(f"  Metrics: {[f'{name} ({pos})' for pos, name in metrics]}")
        print(f"  Zones: {[f'{name} ({pos}±{size})' for pos, size, name in zones]}")
        
        for glyph in font.glyphs:
            layer = glyph.layers[master.id]
            
            if not layer.paths:
                continue
            
            top_nodes, bottom_nodes = get_extreme_nodes(layer)
            
            # Check top nodes
            for node in top_nodes:
                in_zone, zone_name = is_in_alignment_zone(node.y, zones, tolerance)
                on_metric, metric_name = is_on_vertical_metric(node.y, metrics, tolerance)
                
                if not (in_zone or on_metric):
                    affected_by_master[master.id].add(glyph.name)
                    # Add annotation
                    annotation = GSAnnotation()
                    annotation.type = TEXT
                    annotation.text = f"⚠ Top: {int(node.y)}"
                    annotation.position = NSPoint(node.x, node.y)
                    layer.annotations.append(annotation)
            
            # Check bottom nodes
            for node in bottom_nodes:
                in_zone, zone_name = is_in_alignment_zone(node.y, zones, tolerance)
                on_metric, metric_name = is_on_vertical_metric(node.y, metrics, tolerance)
                
                if not (in_zone or on_metric):
                    affected_by_master[master.id].add(glyph.name)
                    # Add annotation
                    annotation = GSAnnotation()
                    annotation.type = TEXT
                    annotation.text = f"⚠ Bottom: {int(node.y)}"
                    annotation.position = NSPoint(node.x, node.y)
                    layer.annotations.append(annotation)
    
    return affected_by_master

def clear_alignment_annotations(font):
    """
    Clear existing alignment annotations (those starting with ⚠).
    """
    for glyph in font.glyphs:
        for layer in glyph.layers:
            if layer.isMasterLayer or layer.isSpecialLayer:
                annotations_to_remove = []
                for annotation in layer.annotations:
                    if annotation.text and annotation.text.startswith("⚠"):
                        annotations_to_remove.append(annotation)
                
                for annotation in annotations_to_remove:
                    layer.annotations.remove(annotation)

# Main execution
font = Glyphs.font

if not font:
    Message("No Font Open", "Please open a font first.", OKButton=None)
else:
    # Clear previous annotations
    print("Clearing previous alignment annotations...")
    clear_alignment_annotations(font)
    
    print("\nChecking top/bottom node alignment...")
    affected_by_master = check_alignment(font, tolerance=1)
    
    total_count = 0
    tabs_opened = 0
    
    # Open separate tab for each master with affected glyphs
    for master in font.masters:
        affected_glyphs = affected_by_master[master.id]
        
        if affected_glyphs:
            sorted_glyphs = sorted(affected_glyphs)
            total_count += len(sorted_glyphs)
            
            print(f"\n{master.name}: {len(sorted_glyphs)} glyphs with misaligned extreme nodes")
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
            "Misaligned Nodes Found",
            f"Found {total_count} glyphs with misaligned extreme nodes across {tabs_opened} master(s).\nMarked with annotations and opened in separate tabs.",
            OKButton=None
        )
    else:
        print("\nAll extreme nodes are properly aligned!")
        Message(
            "All Aligned",
            "All top and bottom nodes are aligned with metrics or zones.",
            OKButton=None
        )