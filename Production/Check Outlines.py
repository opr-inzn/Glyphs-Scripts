# MenuTitle: Check Outline Errors
# -*- coding: utf-8 -*-
"""
Check for outline errors in selected glyphs and report them in the macro panel.
Based on RedArrow-Glyphs by Jens Kutilek.
"""

from __future__ import division, print_function, unicode_literals
import traceback
from Foundation import NSPoint


def check_extremes(layer):
    """Check if all extremum points are present."""
    errors = []
    for path in layer.paths:
        for node in path.nodes:
            if node.type != "offcurve":
                # Check if extremum is missing
                if hasattr(node, "checkExtremes") and node.checkExtremes():
                    errors.append(
                        f"Missing extremum near ({node.position.x:.0f}, "
                        f"{node.position.y:.0f})"
                    )
    return errors


def check_path_direction(layer):
    """Check if path directions are correct."""
    errors = []
    for i, path in enumerate(layer.paths):
        if not path.direction:
            errors.append(f"Path {i} has incorrect direction")
    return errors


def check_overlaps(layer):
    """Check for overlapping paths."""
    errors = []
    # Use Glyphs' built-in overlap detection
    if hasattr(layer, "checkForOverlap") and layer.checkForOverlap():
        errors.append("Overlapping paths detected")
    return errors


def check_open_paths(layer):
    """Check for open/unclosed paths."""
    errors = []
    for i, path in enumerate(layer.paths):
        if not path.closed:
            errors.append(f"Path {i} is open (not closed)")
    return errors


def check_zero_handles(layer):
    """Check for zero-length handles."""
    errors = []
    for path in layer.paths:
        for i, node in enumerate(path.nodes):
            if node.type == "curve" or node.type == "qcurve":
                prev_node = path.nodes[i - 1]
                if prev_node.type == "offcurve":
                    # Check if handle has zero length
                    dx = node.position.x - prev_node.position.x
                    dy = node.position.y - prev_node.position.y
                    if abs(dx) < 1 and abs(dy) < 1:
                        errors.append(
                            f"Zero-length handle at ({node.position.x:.0f}, "
                            f"{node.position.y:.0f})"
                        )
    return errors


def check_duplicate_nodes(layer):
    """Check for duplicate nodes at the same position."""
    errors = []
    for path in layer.paths:
        positions = []
        for node in path.nodes:
            pos = (round(node.position.x, 1), round(node.position.y, 1))
            if pos in positions:
                errors.append(
                    f"Duplicate node at ({node.position.x:.0f}, "
                    f"{node.position.y:.0f})"
                )
            positions.append(pos)
    return errors


def check_stray_points(layer):
    """Check for stray points (paths with only one node)."""
    errors = []
    for i, path in enumerate(layer.paths):
        if len(path.nodes) == 1:
            node = path.nodes[0]
            errors.append(
                f"Stray point at ({node.position.x:.0f}, "
                f"{node.position.y:.0f})"
            )
    return errors


def check_layer(layer, glyph_name):
    """Run all checks on a layer and return errors."""
    all_errors = []

    if not layer.paths:
        return all_errors

    checks = [
        ("Open Paths", check_open_paths),
        ("Path Direction", check_path_direction),
        ("Overlaps", check_overlaps),
        ("Missing Extremes", check_extremes),
        ("Zero Handles", check_zero_handles),
        ("Duplicate Nodes", check_duplicate_nodes),
        ("Stray Points", check_stray_points),
    ]

    for check_name, check_func in checks:
        try:
            errors = check_func(layer)
            if errors:
                all_errors.append(f"  {check_name}:")
                for error in errors:
                    all_errors.append(f"    • {error}")
        except Exception as e:
            all_errors.append(f"  Error running {check_name}: {str(e)}")

    return all_errors


def main():
    """Main function to check selected glyphs."""
    # Open and bring Macro panel to front
    Glyphs.clearLog()
    Glyphs.showMacroWindow()

    font = Glyphs.font

    if not font:
        print("❌ No font open")
        return

    selected_layers = font.selectedLayers

    if not selected_layers:
        print("❌ No glyphs selected")
        return

    print("=" * 60)
    print("OUTLINE ERROR REPORT")
    print("=" * 60)
    print()

    total_errors = 0
    glyphs_with_errors = 0

    for layer in selected_layers:
        glyph = layer.parent
        glyph_name = glyph.name

        errors = check_layer(layer, glyph_name)

        if errors:
            glyphs_with_errors += 1
            total_errors += len([e for e in errors if e.startswith("    •")])
            print(f"🔴 {glyph_name}")
            for error in errors:
                print(error)
            print()
        else:
            print(f"✅ {glyph_name} - No errors found")

    print("=" * 60)
    print(f"Summary: {glyphs_with_errors} glyph(s) with errors")
    print(f"Total issues: {total_errors}")
    print("=" * 60)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"❌ Script error: {str(e)}")
        print(traceback.format_exc())