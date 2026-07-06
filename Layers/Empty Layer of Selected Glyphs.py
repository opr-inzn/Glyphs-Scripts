#MenuTitle: Empty Layer of Selected Glyphs
# -*- coding: utf-8 -*-
__doc__ = """
Empties the current layer of all selected glyphs, including components, paths, and anchors.
Compatible with all Glyphs 3 layer subclasses.
"""

font = Glyphs.font
if font is None:
    print("No font open")
else:
    selectedLayers = font.selectedLayers

    if not selectedLayers:
        print("No glyphs selected")
    else:
        font.disableUpdateInterface()
        try:
            for layer in selectedLayers:
                glyph = layer.parent

                # Detect what exists before clearing
                hasComponents = bool(layer.components)
                hasPaths = bool(layer.paths)
                hasAnchors = bool(layer.anchors)

                # This reliably clears everything in Glyphs 3:
                layer.clear()

                # Reporting
                cleared = []
                if hasComponents: cleared.append("components")
                if hasPaths: cleared.append("paths")
                if hasAnchors: cleared.append("anchors")

                if cleared:
                    print(f"{glyph.name}: cleared {', '.join(cleared)}")
                else:
                    print(f"{glyph.name}: already empty")

            print(f"\nSuccessfully processed {len(selectedLayers)} layer(s)")

        finally:
            font.enableUpdateInterface()
