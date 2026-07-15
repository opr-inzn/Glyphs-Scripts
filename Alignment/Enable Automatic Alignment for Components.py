# MenuTitle: Enable Auto Alignment for Components
# -*- coding: utf-8 -*-
__doc__ = """
Enables automatic alignment for components in the selected glyphs on the current master.
"""

import GlyphsApp

Font = Glyphs.font
currentMasterID = Font.selectedFontMaster.id
selectedGlyphs = [l.parent for l in Font.selectedLayers]

for glyph in selectedGlyphs:
    layer = glyph.layers[currentMasterID]
    for component in layer.components:
        if component.automaticAlignment:
            component.automaticAlignment = True
    glyph.updateGlyphInfo()

Glyphs.showNotification(
    "Enable Auto Alignment",
    f"Auto alignment enabled for components in {len(selectedGlyphs)} glyph(s)."
)
