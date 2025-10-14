#MenuTitle: Set fileName Parameter for Exports
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__="""Set fileName Parameter in Instances, inserting 'Standard' according to widthClass and style name pattern"""

font = Glyphs.font
famName = font.familyName

# Step 1: Check if any instance has widthClass other than 5
hasNonStandardWidth = any(inst.widthClass != 5 for inst in font.instances if inst.active)

for inst in font.instances:
    if not inst.active:
        continue

    # --- Determine localized family name ---
    loclfamName = None
    locParam = None

    # Check for localized family names in custom parameters
    for p in inst.customParameters:
        if p.name == "localizedFamilyNames":
            locParam = p.value
            break

    if locParam and isinstance(locParam, dict):
        # Pick the first localized name (or adjust to prefer a specific language)
        loclfamName = list(locParam.values())[0]

    # Fallback to instance's own familyName, then to font.familyName
    if not loclfamName:
        loclfamName = inst.familyName or famName

    baseName = loclfamName

    styleWords = inst.name.strip().split()

    # Handle 'Standard' insertion if widthClass is 5 and others exist
    if hasNonStandardWidth and inst.widthClass == 5:
        if len(styleWords) == 1:
            # Single word (e.g., "Bold")
            styleWords.insert(0, "Standard")
        elif len(styleWords) > 1:
            if len(styleWords[0]) == 1:
                # First word is a single letter (e.g., "L Light")
                styleWords.insert(1, "Standard")
            else:
                # First word is full (e.g., "Light Oblique")
                styleWords = ["Standard"] + styleWords

    styleName = " ".join(styleWords)
    fileName = "{} {}".format(baseName, styleName)

    inst.customParameters["fileName"] = fileName
