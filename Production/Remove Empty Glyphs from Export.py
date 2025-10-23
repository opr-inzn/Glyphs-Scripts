# MenuTitle: Remove Empty Glyphs from Export
# -*- coding: utf-8 -*-
__doc__ = """
Adds a custom parameter to all instances to remove empty glyphs during
export. Excludes glyphs that are intentionally empty (space, separators,
CR, NULL) and glyphs already set to not export.
"""

# List of glyph names that should be empty
INTENTIONALLY_EMPTY = {
    "space",
    "uni00A0",  # no-break space
    "CR",
    "NULL",
    ".null",
    "nonmarkingreturn",
}


def is_glyph_empty(glyph):
    """Check if a glyph is empty across all masters"""
    if glyph.name in INTENTIONALLY_EMPTY:
        return False

    # Check if glyph is a separator
    if glyph.category == "Separator":
        return False

    # Check if glyph is already set to not export
    if glyph.export == False:
        return False

    for layer in glyph.layers:
        # Check if layer has paths, components, or anchors
        if (
            len(layer.paths) > 0
            or len(layer.components) > 0
            or len(layer.anchors) > 0
        ):
            return False
    return True


def main():
    font = Glyphs.font
    if not font:
        print("No font open")
        Glyphs.showMacroWindow()
        return

    # Find all empty glyphs
    empty_glyphs = []
    for glyph in font.glyphs:
        if is_glyph_empty(glyph):
            empty_glyphs.append(glyph.name)

    if not empty_glyphs:
        print("No empty glyphs found")
        # Remove the parameter if no empty glyphs exist
        for instance in font.instances:
            if "Remove Glyphs" in instance.customParameters:
                del instance.customParameters["Remove Glyphs"]
                print(
                    f"Removed Remove Glyphs parameter from {instance.name}"
                )
        Glyphs.showMacroWindow()
        return

    print(f"Found {len(empty_glyphs)} empty glyphs:")
    print(", ".join(empty_glyphs))

    # Set Remove Glyphs parameter for all instances
    for instance in font.instances:
        # Always overwrite with current list
        instance.customParameters["Remove Glyphs"] = sorted(empty_glyphs)
        print(f"Set Remove Glyphs parameter in {instance.name}")

    print("\nDone! Empty glyphs will be removed during export.")
    
    # Open Macro Panel to show output
    Glyphs.showMacroWindow()


main()