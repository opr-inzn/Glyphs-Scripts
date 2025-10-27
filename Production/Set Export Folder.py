# MenuTitle: Set Export Folder
# -*- coding: utf-8 -*-
__doc__ = """
Sets Export Folder for all instances, preferring localized family names.
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
    family_name = re.sub(r'(?i)(?:v\d+(?:\.\d+)?|lab\d*|\d+)', '', family_name).strip()
    
    style_name = instance.name or ""
    full_name = f"{family_name} {style_name}".strip()
    
    # Clean up multiple spaces
    full_name = re.sub(r' +', ' ', full_name)
    
    try:
        instance.customParameters["Export Folder"] = family_name
    except Exception:
        # In case CustomParametersProxy behaves differently in some builds:
        instance.setCustomParameter_forKey_(family_name, "Export Folder")

print("✅ Export Folder set for all instances, using localized family names where available.")