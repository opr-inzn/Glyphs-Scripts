# MenuTitle: Style Linker
# -*- coding: utf-8 -*-
__doc__ = """
Links upright and italic instances, sets Italic/Bold linkage,
assigns OS/2 weight classes, and synchronises Axis Location (wght) for all instances.
Adds Axis Location only if wght axis value ≠ weightClass.
If no 'Regular' exists, 'Book' is used as the base for Bold links.
Handles Hairline, Thin, Light, Medium, Semibold, ExtraBold, Bold, and Black.
"""

from GlyphsApp import Glyphs, GSCustomParameter
from Foundation import NSDictionary

font = Glyphs.font
if not font:
    raise Exception("No font open.")

# ---------------------------------------------------------
# Helpers
# ---------------------------------------------------------

def is_italic_name(n):
    return n.endswith(" Italic")

def set_linkstyle_safe(inst, name):
    """Set linkStyle safely across Glyphs versions."""
    try:
        if hasattr(inst, "linkStyleName"):
            inst.linkStyleName = name
        if hasattr(inst, "linkStyle"):
            inst.linkStyle = name
    except Exception as e:
        print(f"⚠️ Could not set linkStyle for '{inst.name}': {e}")

def detect_weight_class(name, all_names):
    """Determine OS/2 weight class based on instance name and available names."""
    name = name.lower()
    has_hairline = any("hairline" in n.lower() for n in all_names)
    has_thin = any("thin" in n.lower() for n in all_names)

    if "hairline" in name:
        return 100 if has_thin else 250
    if "thin" in name:
        return 250 if has_hairline else 100
    if "light" in name:
        return 300
    if "medium" in name:
        return 500
    if "semibold" in name or "demibold" in name:
        return 600
    if "extrabold" in name or "heavy" in name:
        return 800
    if "bold" in name:
        return 700
    if "black" in name or "ultrablack" in name:
        return 900
    return None

def get_weight_axis_value(inst):
    """Try to read the wght axis value safely."""
    try:
        if hasattr(inst, "axes") and inst.axes:
            if len(inst.axes) > 0:
                val = inst.axes[0]
                if isinstance(val, (int, float)):
                    return float(val)
    except Exception:
        pass
    return None


def ensure_axis_location_only_if_needed(inst, wc):
    """
    Add 'Axis Location' [{Axis: "wght", Location: weightClass}]
    only if axis value ≠ weightClass.
    Remove existing one if they match.
    """
    axis_val = get_weight_axis_value(inst)
    current_param = None
    if inst.customParameters:
        for p in inst.customParameters:
            if p.name == "Axis Location":
                current_param = p
                break

    # Case 1: Axis value matches weightClass → remove redundant entry
    if axis_val is not None and round(axis_val) == int(wc):
        if current_param:
            inst.customParameters.remove(current_param)
            print(f"Removed redundant Axis Location from '{inst.name}' (wght matches {wc})")
        return False

    # Case 2: Axis value differs → add Axis Location in correct Glyphs format
    if axis_val is not None and round(axis_val) != int(wc):
        if current_param:
            inst.customParameters.remove(current_param)

        # Glyphs expects a list of dicts, not a dict itself
        axis_value = [{"Axis": "Weight", "Location": int(wc)}]
        inst.customParameters.append(GSCustomParameter("Axis Location", axis_value))
        print(f"Set Axis Location Weight={wc} for '{inst.name}' (axis={axis_val})")
        return True

    # Case 3: No axis info → skip
    return False



instances_by_name = {inst.name.strip(): inst for inst in font.instances}
all_names = list(instances_by_name.keys())

linked_count = 0
weight_set_count = 0
bold_linked_count = 0
axis_fixed_count = 0

# ---------------------------------------------------------
# 1. Italic linking
# ---------------------------------------------------------

for inst in font.instances:
    base_name = inst.name.strip()
    if is_italic_name(base_name):
        continue

    italic_name = f"{base_name} Italic"
    italic = instances_by_name.get(italic_name)

    if italic:
        before_is_italic = getattr(italic, "isItalic", False)
        before_link = getattr(italic, "linkStyle", None)

        italic.isItalic = True
        set_linkstyle_safe(italic, base_name)

        after_is_italic = getattr(italic, "isItalic", False)
        after_link = getattr(italic, "linkStyle", None)

        if (after_is_italic != before_is_italic) or (after_link != before_link):
            linked_count += 1
            print(f"Linked '{italic.name}' → '{base_name}' (italic enabled)")

# ---------------------------------------------------------
# 2. Weight classes + Axis Locations (all instances)
# ---------------------------------------------------------

for inst in font.instances:
    wc = detect_weight_class(inst.name, all_names)
    if wc is not None:
        if getattr(inst, "weightClass", None) != wc:
            inst.weightClass = wc
            weight_set_count += 1
            print(f"Set WeightClass {wc} for '{inst.name}'")

        if ensure_axis_location_only_if_needed(inst, wc):
            axis_fixed_count += 1

# ---------------------------------------------------------
# 3. Bold linkage (Regular or Book)
# ---------------------------------------------------------

base = instances_by_name.get("Regular") or instances_by_name.get("Book")
bold = instances_by_name.get("Bold")
bold_italic = instances_by_name.get("Bold Italic")

if base and bold:
    bold.isBold = True
    set_linkstyle_safe(bold, base.name)
    bold_linked_count += 1
    print(f"Linked 'Bold' as Bold of {base.name}")

if base and bold_italic:
    bold_italic.isBold = True
    set_linkstyle_safe(bold_italic, base.name)
    bold_linked_count += 1
    print(f"Linked 'Bold Italic' as Bold of {base.name}")

# ---------------------------------------------------------
# 4. Summary
# ---------------------------------------------------------

Glyphs.showNotification(
    "Style Linker Finished",
    f"Linked {linked_count} italics, set {weight_set_count} weights, "
    f"linked {bold_linked_count} bolds, updated {axis_fixed_count} Axis Locations "
    f"(base: {base.name if base else 'none'})."
)
print(
    f"✅ Linked {linked_count} italics | Set {weight_set_count} weights | "
    f"Linked {bold_linked_count} bolds | Updated {axis_fixed_count} Axis Locations "
    f"(base: {base.name if base else 'none'})."
)
