# MenuTitle: Duplicate All Instances for Trial Export
# -*- coding: utf-8 -*-

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

if font.instances:
    original_count = len(font.instances)
    
    for i in range(original_count):
        instance = font.instances[i]
        
        # Skip variable font settings
        if instance.type == INSTANCETYPEVARIABLE:
            continue
        
        # Create a copy of the instance
        new_instance = instance.copy()
        
        # Get the original family name
        if instance.customParameters["familyName"]:
            original_family = instance.customParameters["familyName"]
        else:
            original_family = font.familyName
        
        # Remove numbers from family name
        original_family = re.sub(r'\d+', '', original_family).strip()
        
        # Set the trial family name
        trial_family = original_family + " Unlicensed Trial"
        style_name = new_instance.name or ""
        full_name = f"{trial_family} {style_name}".strip()
        
        # Clean up multiple spaces
        full_name = re.sub(r' +', ' ', full_name)
        trial_family = re.sub(r' +', ' ', trial_family)
        
        # Set custom parameter for family name
        new_instance.customParameters["familyName"] = trial_family
        
        # Set localized family name
        new_instance.setProperty_value_languageTag_("familyNames", trial_family, None)
        
        # Set postscript full name
        new_instance.setProperty_value_languageTag_("postscriptFullNames", full_name, None)
        
        # Clean up fontName - replace spaces with hyphens and remove consecutive hyphens
        font_name = full_name.replace(" ", "-")
        font_name = re.sub(r'-+', '-', font_name)
        new_instance.fontName = font_name
        
        # Add the new instance to the font
        font.instances.append(new_instance)
        
    print("✅ Duplicated %d instance(s) with 'Unlicensed Trial' family name" % original_count)
else:
    print("No instances found")