# MenuTitle: Duplicate All Instances for Trial Export (Hide in Preview)
# -*- coding: utf-8 -*-
__doc__ = """
Duplicates all non-variable instances as “Unlicensed Trial” versions.
After duplication, hides all trial instances from the preview window (👁)
but keeps them active for export.
"""

from GlyphsApp import Glyphs
import unicodedata
import re

font = Glyphs.font
if not font:
    print("No font open.")
    raise SystemExit

# ---------- helpers ----------

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
    return False

def clean_family_name(name):
    """Remove version numbers, LAB tags, and digits from family name."""
    if not name:
        return ""
    name = re.sub(r"(?i)(?:v\\d+(?:\\.\\d+)?|lab\\d*|\\d+)", "", name)
    name = re.sub(r"[\\s\\-\\._]+$", "", name).strip()
    return name

# ---------- duplication ----------

all_instances = list(font.instances)
created_count = 0
existing_keys = set()

# record existing instance identifiers
for i in all_instances:
    fam = normalize_name(get_family_name(i))
    style = normalize_name(i.name)
    key = f"{fam}::{style}"
    existing_keys.add(key)

# duplicate non-trial, non-variable
try:
    from GlyphsApp import INSTANCETYPEVARIABLE
    originals = [i for i in all_instances if not is_trial_instance(i) and i.type != INSTANCETYPEVARIABLE]
except Exception:
    originals = [i for i in all_instances if not is_trial_instance(i)]

for instance in originals:
    base_family = get_family_name(instance) or font.familyName
    base_family = clean_family_name(base_family)
    trial_family = f"{base_family} Unlicensed Trial"
    style_name = instance.name or ""
    full_name = f"{trial_family} {style_name}".strip()

    trial_key = f"{normalize_name(trial_family)}::{normalize_name(style_name)}"
    if trial_key in existing_keys:
        continue

    new_instance = instance.copy()
    # set trial naming
    new_instance.setProperty_value_languageTag_("familyNames", trial_family, None)
    new_instance.setProperty_value_languageTag_("postscriptFullNames", full_name, None)
    font_name = re.sub(r"-+", "-", full_name.replace(" ", "-"))
    new_instance.fontName = font_name
    new_instance.customParameters["Export Folder"] = trial_family

    font.instances.append(new_instance)
    existing_keys.add(trial_key)
    created_count += 1

# ---------- hide trials from preview ----------

hidden_count = 0
for inst in font.instances:
    fam = get_family_name(inst)
    if isinstance(fam, str) and "unlicensed trial" in fam.lower():
        try:
            inst.visible = False    # hide from 👁 preview
            hidden_count += 1
        except Exception as e:
            print(f"⚠️ Could not hide {inst.name}: {e}")

# ---------- summary ----------

if created_count:
    print(f"✅ Created {created_count} new 'Unlicensed Trial' instance(s).")
else:
    print("⚠️ All trial instances already exist — nothing to duplicate.")

print(f"👁 Hidden {hidden_count} 'Unlicensed Trial' instance(s) from preview.")
Glyphs.showNotification(
    "Duplicate + Hide Trials",
    f"Created {created_count}, hidden {hidden_count} 'Unlicensed Trial' instances."
)