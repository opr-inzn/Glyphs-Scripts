# MenuTitle: Disable Auto Alignment for Components in Selected Glyphs on Current Master
# -*- coding: utf-8 -*-
__doc__ = """
Disables automatic alignment for components in the selected glyphs on the current master.
"""

import GlyphsApp

Font = Glyphs.font
currentMasterID = Font.selectedFontMaster.id
selectedGlyphs = [l.parent for l in Font.selectedLayers]

for glyph in selectedGlyphs:
    layer = glyph.layers[currentMasterID]
    for component in layer.components:
        if component.automaticAlignment:
            component.automaticAlignment = False
    glyph.updateGlyphInfo()

Glyphs.showNotification(
    "Disable Auto Alignment",
    f"Auto alignment disabled for components in {len(selectedGlyphs)} glyph(s)."
)
