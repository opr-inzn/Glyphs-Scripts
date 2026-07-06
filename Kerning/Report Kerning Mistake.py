# MenuTitle: Report Kerning Mistakes
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals

__doc__ = """
Finds unnecessary kernings and groupings, and opens all questionable pairs in
new tabs for active master. Expands group sides to key glyphs.
"""

from GlyphsApp import Glyphs

thisFont = Glyphs.font  # frontmost font
if not thisFont:
    raise Exception("No frontmost font. Open a font and try again.")

# --- config from your original ------------------------------------------------

extensionsWithoutKerning = (".tf", ".tosf")
noKerningToTheLeft = (
    "jacute", "Jacute", "bullet", "copyright", "parenleft", "bracketleft",
    "braceleft", "section", "questiondown", "exclamdown",
)
noKerningToTheRight = (
    "ldot", "Ldot", "trademark", "registered", "parenright", "bracketright",
    "braceright", "degree", "percent", "perthousand", "ordfeminine", "ordmasculine",
)

extensionsUnlikelyToBeKerned = ("comb",)
glyphNamesWithExtensionsNotToBeKerned = []
for extension in extensionsWithoutKerning:
    extensionNames = [
        g.name for g in thisFont.glyphs
        if extension in g.name and not g.name.startswith(extension)
    ]
    glyphNamesWithExtensionsNotToBeKerned += extensionNames

unlikelyToBeKerned = (
    "notequal","brokenbar","divide","yen","radical","dollar","currency","asciitilde",
    "emptyset","increment","trademark","dagger","estimated","florin","copyright",
    "partialdiff","section","less","percent","cent","ampersand","perthousand","Delta",
    "lessequal","pi","Omega","sterling","product","infinity","greater","degree",
    "approxequal","integral","registered","numero","daggerdbl","plusminus","multiply",
    "asciicircum","dbldagger","leftArrow","euro","Ohm","greaterequal","bar","lozenge",
    "literSign","equal","logicalnot","micro","paragraph","plus",".notdef","published",
    "at","minus","rightArrow",
)
dontKernThese = unlikelyToBeKerned + tuple(glyphNamesWithExtensionsNotToBeKerned)

leftGroupsToBeChecked = [
    g.leftKerningGroup for g in thisFont.glyphs
    if g.leftKerningGroup and g.name in dontKernThese
]
rightGroupsToBeChecked = [
    g.rightKerningGroup for g in thisFont.glyphs
    if g.rightKerningGroup and g.name in dontKernThese
]

# --- helpers ------------------------------------------------------------------

def safeGlyphByName(name):
    try:
        return thisFont.glyphs[name]
    except Exception:
        return None

def glyphNameFromId(gid):
    g = thisFont.glyphForId_(gid)
    return g.name if g else None

def groupKeyGlyphName(groupName):
    # groupName like "@MMK_L_A" or "@MMK_R_n"
    # Find the glyph whose kerning group equals the groupName’s suffix
    if not groupName or groupName[0] != "@":
        return None
    try:
        isLeft = groupName.startswith("@MMK_L_")
        key = groupName.split("_", 2)[-1]  # suffix after @MMK_L_ / @MMK_R_
        for g in thisFont.glyphs:
            if isLeft and g.leftKerningGroup == key:
                return g.name
            if (not isLeft) and g.rightKerningGroup == key:
                return g.name
    except Exception:
        pass
    return None

def humanReadableName(side):
    if not side:
        return "???"
    if side[0] == "@":
        return "@%s" % side[7:]
    name = glyphNameFromId(side)
    return name or side

def reportBadKernPair(leftSide, rightSide, kernValue):
    print("  Questionable pair: %s -- %s (%i)" % (
        humanReadableName(leftSide), humanReadableName(rightSide), kernValue
    ))

def makeConcretePairString(leftSide, rightSide):
    # Accept glyph id or group. Convert to glyph names using key glyphs for groups.
    if leftSide and leftSide[0] == "@":
        leftName = groupKeyGlyphName(leftSide)
    else:
        leftName = glyphNameFromId(leftSide)
    if rightSide and rightSide[0] == "@":
        rightName = groupKeyGlyphName(rightSide)
    else:
        rightName = glyphNameFromId(rightSide)
    if leftName and rightName:
        return "/%s/%s" % (leftName, rightName)
    return None

def openPairsInTabs(pairs, masterIndex, chunkSize=300):
    if not pairs:
        print("  No concrete glyph pairs collected for this master; no tab opened.")
        return
    for i in range(0, len(pairs), chunkSize):
        text = " ".join(pairs[i:i+chunkSize])
        tab = None
        # Try preferred API
        try:
            tab = thisFont.newTab(text)
        except Exception:
            tab = None
        # Fallback API
        if tab is None:
            try:
                doc = Glyphs.currentDocument
                if doc and doc.windowController():
                    tab = doc.windowController().addTabWithString_(text)
            except Exception:
                tab = None
        if tab:
            try:
                tab.masterIndex = masterIndex
            except Exception:
                pass

# --- run ---------------------------------------------------------------------

Glyphs.clearLog()
Glyphs.showMacroWindow()

print("PROBLEMS WITH KERN PAIRS:")

for masterIndex, master in enumerate(thisFont.masters):
    print("\n  MASTER: %s" % master.name)
    kerning = thisFont.kerning.get(master.id, {})
    pairsForTab = []

    # Left: specific glyphs that shouldn't be on left
    leftBlock = noKerningToTheRight + unlikelyToBeKerned + tuple(glyphNamesWithExtensionsNotToBeKerned)
    for leftGlyphName in leftBlock:
        gLeft = safeGlyphByName(leftGlyphName)
        if not gLeft:
            continue
        leftID = gLeft.id
        rightDict = kerning.get(leftID, {})
        for rightSide, value in rightDict.items():
            reportBadKernPair(leftID, rightSide, value)
            pairStr = makeConcretePairString(leftID, rightSide)
            if pairStr:
                pairsForTab.append(pairStr)

    # Right: specific glyphs that shouldn't be on right, and flagged groups
    shouldntRight = noKerningToTheLeft + unlikelyToBeKerned + tuple(glyphNamesWithExtensionsNotToBeKerned)
    for leftSide, rightDict in kerning.items():
        for rightSide, value in rightDict.items():
            if rightSide and rightSide[0] != "@":
                rg = thisFont.glyphForId_(rightSide)
                if rg and rg.name in shouldntRight:
                    reportBadKernPair(leftSide, rightSide, value)
                    pairStr = makeConcretePairString(leftSide, rightSide)
                    if pairStr:
                        pairsForTab.append(pairStr)
            elif rightSide and rightSide.replace("@MMK_R_", "@") in leftGroupsToBeChecked:
                reportBadKernPair(leftSide, rightSide, value)
                pairStr = makeConcretePairString(leftSide, rightSide)
                if pairStr:
                    pairsForTab.append(pairStr)

    # Left groups corresponding to questionable right groups
    for leftGroup in ["@MMK_L_%s" % group for group in rightGroupsToBeChecked]:
        rightDict = kerning.get(leftGroup, {})
        for rightSide, value in rightDict.items():
            reportBadKernPair(leftGroup, rightSide, value)
            pairStr = makeConcretePairString(leftGroup, rightSide)
            if pairStr:
                pairsForTab.append(pairStr)

    openPairsInTabs(pairsForTab, masterIndex)

print("\nDone. If no tabs opened, check the Macro window for logs/explanations.")