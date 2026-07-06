# MenuTitle: Hide Trial Instances from Preview
# -*- coding: utf-8 -*-
__doc__ = """
Hides all instances from the preview window (👁) whose familyName
contains “Unlicensed” or “Trial”. Keeps them active for export.
"""

from GlyphsApp import Glyphs

font = Glyphs.font
if not font:
    raise Exception("No font open in Glyphs.")

KEYWORDS = ("unlicensed", "trial")

hidden = 0
for inst in font.instances:
    fam = inst.familyName
    if isinstance(fam, str) and any(k in fam.lower() for k in KEYWORDS):
        try:
            inst.visible = False   # 👁 off in preview
            hidden += 1
            print(f"👁‍🗨 Hidden from preview: {inst.name}")
        except Exception as e:
            print(f"⚠️ Could not hide {inst.name}: {e}")
    else:
        print(f"– Still visible: {inst.name}")

print(f"\nHidden {hidden} instance(s) from preview containing 'Unlicensed' or 'Trial'.")
Glyphs.showNotification(
    "Hide Trial Instances from Preview",
    f"Hidden {hidden} instance(s)."
)
