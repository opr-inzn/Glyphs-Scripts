# MenuTitle: Add Font Info Parameters
# -*- coding: utf-8 -*-

from datetime import datetime
font = Glyphs.font

if not font:
    print("No font open!")
else:
    from GlyphsApp import GSCustomParameter

    current_year = datetime.now().year

    # General Info
    font.designer = "Maximilian Inzinger"
    font.designerURL = "www.maximilianinzinger.com"
    font.manufacturer = "Office of Personal Responsibility"
    font.manufacturerURL = "www.maximilianinzinger.com"
    font.license = (
        "The fonts and data enclosed in the font files may only be used according to the Office of Personal Responsibility EULA, which strictly prohibits any modifications, reassembling, renaming, storing on publicly accessible servers, redistributing, or selling. Unauthorized use of this typographic software will result in legal consequences. For further inquiries, please contact office@maximilianinzinger.com."
    )
    font.copyright = (
        f"Copyright (c) {current_year} by Office of Personal Responsibility (Maximilian Inzinger). All rights reserved."
    )

    font.properties["vendorID"] = "OPR"
    font.properties["licenseURL"] = "https://maximilianinzinger.com/license"
    font.properties["versionString"] = "Version %d.%03d"

    # Font-level custom parameters
    font.customParameters["Use Typo Metrics"] = True
    if len(font.masters) > 1: 
        font.customParameters["Family Alignment Zones"] = []
    font.customParameters["panose"] = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    font.customParameters["fsType"] = 3 # 0 = Editable embedding

    # Optional disabled parameters
    # Check for existing unicodeRanges
    if not any(p.name == "unicodeRanges" for p in font.customParameters):
        unicodeRanges = GSCustomParameter("unicodeRanges", [])
        unicodeRanges.active = False
        font.customParameters.append(unicodeRanges)
    else:
        print("ℹ️ 'unicodeRanges' already exists — skipping.")

    # Check for existing codePageRanges
    if not any(p.name == "codePageRanges" for p in font.customParameters):
        codePageRanges = GSCustomParameter("codePageRanges", [])
        codePageRanges.active = False
        font.customParameters.append(codePageRanges)
    else:
        print("ℹ️ 'codePageRanges' already exists — skipping.")
        
    font.customParameters["Update Features"] = True
    
    param_name = "Enforce Compatibility Check"
    param_value = True
    
    font.customParameters = [
        cp for cp in font.customParameters if cp.name != param_name
    ]

    if len(font.masters) > 1: 
        font.customParameters.append(GSCustomParameter(param_name, param_value))

    print("✅ Font info parameters added.")
