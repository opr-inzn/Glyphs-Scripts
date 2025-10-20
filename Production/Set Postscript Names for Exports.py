# MenuTitle: Set Postscript Names for Exports
# -*- coding: utf-8 -*-
__doc__ = """
Sets Postscript names for all instances, preferring localized family names.
"""

import unicodedata
import re

font = Glyphs.font
if not font:
    print("No font open.")
    raise SystemExit

def ascii_ps_name(s):
    s = unicodedata.normalize("NFKD", s)
    s = "".join(c for c in s if ord(c) < 128 and not c.isspace())
    return s

def get_localized_family(instance):
    # Check if instance has localized familyNames property
    if instance.properties:
        for prop in instance.properties:
            if prop.key == "familyNames":
                # Found localized family names, use the default value
                if prop.defaultValue:
                    return prop.defaultValue
    
    # Fallback to custom parameter or font family
    return instance.customParameters["familyName"] or font.familyName

for instance in font.instances:
    family_name = get_localized_family(instance)
    
    # Remove numbers from family name
    family_name = re.sub(r'\d+', '', family_name).strip()
    
    style_name = instance.name or ""
    full_name = f"{family_name} {style_name}".strip()
    
    # Clean up multiple spaces
    full_name = re.sub(r' +', ' ', full_name)

    # Set postscriptFullNames at Default language (use None for "Default")
    instance.setProperty_value_languageTag_("postscriptFullNames", full_name, None)
    
    # Clean up fontName - replace spaces with hyphens and remove consecutive hyphens
    font_name = full_name.replace(" ", "-")
    font_name = re.sub(r'-+', '-', font_name)  # Replace multiple hyphens with single hyphen
    instance.fontName = font_name

print("✅ postscriptFullNames set for all exports, using localized family names where available.")