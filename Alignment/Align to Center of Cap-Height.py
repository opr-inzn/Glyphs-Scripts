# MenuTitle: Align Selected Glyphs to Center (Cap Height)
# -*- coding: utf-8 -*-
__doc__ = """
Aligns each selected glyph so its vertical center matches the cap height center,
while preserving sidebearings numerically. Works with italic/slanted masters.
"""

from GlyphsApp import Glyphs
from math import radians, tan

def alignSelectedGlyphsToCapCenter():
    font = Glyphs.font
    if not font:
        print("⚠️ No font open.")
        return

    font.disableUpdateInterface()

    for layer in font.selectedLayers:
        glyph = layer.parent
        master = layer.master
        capCenterY = master.capHeight * 0.5

        # Italic angle (negative in right-leaning italics)
        italicAngle = getattr(master, "italicAngle", 0.0)
        italicTan = tan(radians(-italicAngle)) if italicAngle else 0.0

        # Store sidebearings to restore later
        old_LSB = layer.LSB
        old_RSB = layer.RSB

        # Layer bounds
        bounds = layer.bounds
        layerMinY = bounds.origin.y
        layerMaxY = bounds.origin.y + bounds.size.height
        layerCenterY = (layerMinY + layerMaxY) * 0.5

        deltaY = capCenterY - layerCenterY
        deltaX = deltaY * italicTan  # move along italic slant

        if abs(deltaY) < 0.01:
            print(f"{glyph.name}: already centered.")
            continue

        # Move paths
        for path in layer.paths:
            for node in path.nodes:
                node.x += deltaX
                node.y += deltaY

        # Move components
        for comp in layer.components:
            pos = comp.position
            comp.position = (pos.x + deltaX, pos.y + deltaY)

        # Move anchors
        for anchor in layer.anchors:
            pos = anchor.position
            anchor.position = (pos.x + deltaX, pos.y + deltaY)

        # Restore sidebearings exactly
        layer.LSB = old_LSB
        layer.RSB = old_RSB

        print(f"✅ {glyph.name}: shifted by ({deltaX:.2f}, {deltaY:.2f}) along italic angle")

    font.enableUpdateInterface()
    Glyphs.showNotification(
        "Align Glyphs",
        "Selected glyphs aligned to cap height center."
    )

alignSelectedGlyphsToCapCenter()