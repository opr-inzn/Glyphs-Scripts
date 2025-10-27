# MenuTitle: Duplicate All Instances for Trial Export
# -*- coding: utf-8 -*-

import unicodedata
import re

font = Glyphs.font
if not font:
    print("No font open.")
    raise SystemExit

def normalize_name(s):
    """Simplify a string for consistent comparison."""
    if not s:
        return ""
    s = unicodedata.normalize("NFKD", s)
    s = re.sub(r"\s+", " ", s.strip().lower())
    return s

def get_family_name(inst):
    """Return best possible family name string for an instance."""
    fam = None
    try:
        fam = inst.customParameters["familyName"]
    except Exception:
        pass
    if not fam:
        fam = getattr(inst, "familyName", None)
    return fam or ""

def is_trial_instance(inst):
    """Return True if this instance is a trial version."""
    fam = get_family_name(inst)
    if "unlicensed trial" in fam.lower():
        return True
    try:
        loc_name = inst.propertyForKey_("familyNames")
        if isinstance(loc_name, str) and "unlicensed trial" in loc_name.lower():
            return True
    except Exception:
        pass
    return False

def clean_family_name(name):
    """Remove version numbers, LAB tags, and digits from family name."""
    if not name:
        return ""
    # Remove version-like parts (v0.7, V1, v1.0), LAB variants, and standalone digits
    name = re.sub(r'(?i)(?:v\d+(?:\.\d+)?|lab\d*|\d+)', '', name)
    # Remove stray punctuation or hyphens left behind
    name = re.sub(r'[\s\-\._]+$', '', name).strip()
    return name

if font.instances:
    all_instances = list(font.instances)
    created_count = 0

    # Build a normalized registry of all existing instances (family + style)
    existing_keys = set()
    for i in all_instances:
        fam = normalize_name(get_family_name(i))
        style = normalize_name(i.name)
        key = f"{fam}::{style}"
        existing_keys.add(key)

    # Iterate over original (non-trial, non-variable) instances
    originals = [i for i in all_instances if not is_trial_instance(i) and i.type != INSTANCETYPEVARIABLE]

    for instance in originals:
        base_family = get_family_name(instance) or font.familyName
        base_family = clean_family_name(base_family)
        trial_family = f"{base_family} Unlicensed Trial"
        style_name = instance.name or ""
        full_name = f"{trial_family} {style_name}".strip()

        # Normalized lookup key for the potential trial version
        trial_key = f"{normalize_name(trial_family)}::{normalize_name(style_name)}"

        if trial_key in existing_keys:
            continue  # already exists

        # Duplicate and rename
        new_instance = instance.copy()
        new_instance.setProperty_value_languageTag_("familyNames", trial_family, None)
        new_instance.setProperty_value_languageTag_("postscriptFullNames", full_name, None)

        font_name = re.sub(r'-+', '-', full_name.replace(" ", "-"))
        new_instance.fontName = font_name
        
        new_instance.customParameters["Export Folder"] = trial_family

        font.instances.append(new_instance)
        existing_keys.add(trial_key)
        created_count += 1

    if created_count:
        print(f"✅ Created {created_count} new 'Unlicensed Trial' instance(s).")
    else:
        print("⚠️ All trial instances already exist — nothing to duplicate.")
else:
    print("No instances found.")
