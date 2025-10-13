#MenuTitle: Clear All Annotations
# -*- coding: utf-8 -*-

"""
Clears all annotations from all glyphs in all masters and special layers.
"""

from GlyphsApp import Glyphs, Message

def clear_all_annotations(font):
    """
    Clear all annotations from all layers in the font.
    Returns the total count of removed annotations.
    """
    total_removed = 0
    glyphs_affected = 0
    
    for glyph in font.glyphs:
        glyph_had_annotations = False
        
        for layer in glyph.layers:
            if layer.annotations:
                count = len(layer.annotations)
                if count > 0:
                    glyph_had_annotations = True
                    total_removed += count
                    # Clear all annotations
                    layer.annotations = []
        
        if glyph_had_annotations:
            glyphs_affected += 1
    
    return total_removed, glyphs_affected

# Main execution
font = Glyphs.font

if not font:
    Message("No Font Open", "Please open a font first.", OKButton=None)
else:
    print("Clearing all annotations...")
    
    removed_count, glyphs_count = clear_all_annotations(font)
    
    if removed_count > 0:
        print(f"\nCleared {removed_count} annotations from {glyphs_count} glyphs.")
        Message(
            "Annotations Cleared",
            f"Cleared {removed_count} annotations from {glyphs_count} glyphs.",
            OKButton=None
        )
    else:
        print("\nNo annotations found.")
        Message(
            "No Annotations",
            "No annotations were found in this font.",
            OKButton=None
        )