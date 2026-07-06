# -*- coding: utf-8 -*-
#MenuTitle: Compare Kerning Pairs

from GlyphsApp import Glyphs, GSControlLayer

font = Glyphs.font
if not font or len(font.masters) < 2:
    raise Exception("Open a font with at least two masters.")

masterA = font.masters[0]
masterB = font.masters[1]

kernA = font.kerning.get(masterA.id, {})
kernB = font.kerning.get(masterB.id, {})

def allPairs(kernDict):
    pairs = set()
    for L, rights in kernDict.items():
        for R in rights.keys():
            pairs.add((L, R))
    return pairs

pairsA = allPairs(kernA)
pairsB = allPairs(kernB)

onlyInA = pairsA - pairsB
onlyInB = pairsB - pairsA

tab = font.newTab()
tab.text = ""
tab.graphicView().setDoKerning_(1)
tab.graphicView().setDoSpacing_(0)

def glyphName(name, isLeft):
    if name.startswith("@"):
        group = name[7:]
        for g in font.glyphs:
            if isLeft and g.rightKerningGroup == group:
                return g.name
            if not isLeft and g.leftKerningGroup == group:
                return g.name
        return None
    else:
        g = font.glyphForId_(name)
        return g.name if g else None

def addHeader(text):
    for c in text:
        g = font.glyphForCharacter_(ord(c))
        if g:
            tab.layers.append(g.layers[masterA.id])
    tab.layers.append(GSControlLayer.newline())

def addPairs(pairs, masterID):
    for L, R in sorted(pairs):
        leftName = glyphName(L, isLeft=True)
        rightName = glyphName(R, isLeft=False)
        if not leftName or not rightName:
            continue
        tab.layers.append(font.glyphs[leftName].layers[masterID])
        tab.layers.append(font.glyphs[rightName].layers[masterID])
        tab.layers.append(font.glyphs["space"].layers[masterID])
    tab.layers.append(GSControlLayer.newline())

if onlyInA:
    addHeader(f"Only in {masterA.name}:")
    addPairs(onlyInA, masterA.id)

if onlyInB:
    addHeader(f"Only in {masterB.name}:")
    addPairs(onlyInB, masterB.id)

print(f"Done. {len(onlyInA)} pairs only in {masterA.name}, {len(onlyInB)} only in {masterB.name}.")
