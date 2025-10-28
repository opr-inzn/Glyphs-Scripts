# MenuTitle: Set Postscript Names for Exports
# -*- coding: utf-8 -*-
__doc__ = """
Sets PostScript names for all instances, preferring localized family names.
Adds VariationsPostScriptNamePrefix for variable fonts.
Also sets Style Map Family/Style Names and fileName (custom parameter, no numbers, no spaces).
Cleans Export Folder names of version numbers and LAB tags.
"""

from GlyphsApp import INSTANCETYPEVARIABLE
import unicodedata
import re

font = Glyphs.font
if not font:
    print("No font open.")
    raise SystemExit


def ascii_ps_name(s):
    s = unicodedata.normalize("NFKD", s)
    return "".join(c for c in s if ord(c) < 128 and not c.isspace())


def sanitize_name(s, for_folder=False):
    """
    Remove version numbers, LAB tags, etc.
    Replace spaces with hyphens unless for_folder=True.
    """
    s = re.sub(r"(?i)(?:v\d+(?:\.\d+)?|lab\d*|\d+)", "", s)
    s = s.strip()
    if not for_folder:
        s = re.sub(r"\s+", "-", s)
    s = re.sub(r"-+", "-", s)
    return s.strip("-").strip()


def get_localized_family(instance):
    """Return localized or fallback family name safely."""
    if instance.properties:
        for prop in instance.properties:
            if prop.key == "familyNames" and prop.defaultValue:
                return prop.defaultValue
    try:
        if "familyName" in instance.customParameters:
            return instance.customParameters["familyName"]
    except Exception:
        pass
    return font.familyName


for instance in font.instances:
    family_name = get_localized_family(instance)
    style_name = instance.name or ""

    # Remove redundant “Variable”
    family_name = re.sub(r"(?i)\bvariable\b", "", family_name).strip()
    style_name = re.sub(r"(?i)\bvariable\b", "", style_name).strip()

    # Base full name
    full_name = f"{family_name} {style_name}".strip()
    full_name = re.sub(r" +", " ", full_name)
    font_name = sanitize_name(full_name)

    # --- Shared setup ---
    instance.setProperty_value_languageTag_("postscriptFullNames", full_name, None)
    instance.fontName = font_name

    if instance.type == INSTANCETYPEVARIABLE:
        # Prefix for variable export
        prefix_base = re.sub(r"[\d\s-]+", "", font.familyName)
        variable_prefix = f"{prefix_base}Variable"
        instance.setProperty_value_languageTag_("variationsPostScriptNamePrefix", variable_prefix, None)

        # Variable-specific names
        var_family_name = f"{family_name} Variable"
        var_full_name = f"{family_name} Variable {style_name}".strip()
        var_ps_name = sanitize_name(var_full_name)

        # Family / Full / PS / StyleMap
        instance.setProperty_value_languageTag_("familyNames", var_family_name, None)
        instance.setProperty_value_languageTag_("postscriptFullNames", var_full_name, None)
        instance.setProperty_value_languageTag_("styleMapFamilyNames", var_family_name, None)
        instance.setProperty_value_languageTag_("styleMapStyleNames", style_name, None)
        instance.setProperty_value_languageTag_("preferredFamilyNames", var_family_name, None)
        instance.setProperty_value_languageTag_("preferredSubfamilyNames", style_name, None)

        # File name (custom parameter)
        instance.customParameters["fileName"] = sanitize_name(f"{font.familyName}-Variable-{style_name}")

    else:
        # Static instance setup
        clean_folder_name = sanitize_name(family_name, for_folder=True)
        instance.customParameters["Export Folder"] = clean_folder_name
        instance.customParameters["fileName"] = sanitize_name(f"{font.familyName}-{style_name}")

print("✅ All PostScript, Style Map, fileName, and Export Folder names set cleanly.")
