# MenuTitle: Round Kerning to 5
# encoding: utf-8

__doc__ = """
Rounds the kerning values to the nearest multiple of 5.

In addition, values smaller than MIN_VALUE are erased.
"""

MIN_VALUE = 5

from GlyphsApp import *
font = Glyphs.font

def myround(x, base=5):
    return int(base * round(float(x) / base))

printString = """"""

for eachFontMaster in font.masters:
    eachFontMasterId = eachFontMaster.id
    to_be_removed = []

    for first, seconds in dict(font.kerning[eachFontMasterId]).items():
        # normalize first side
        if isinstance(first, int):
            firstName = font.glyphForId_(first).name
        else:
            firstName = first

        for second, existingValue in dict(seconds).items():
            # normalize second side
            if isinstance(second, int):
                secondName = font.glyphForId_(second).name
            else:
                secondName = second

            # round towards 5
            value = myround(existingValue, 5)

            if abs(existingValue) < MIN_VALUE:
                to_be_removed.append((firstName, secondName, existingValue))
            elif existingValue != value:
                font.setKerningForPair(eachFontMasterId, firstName, secondName, value)
                printString += "%s\t%s: %s, %s, %s\n" % (
                    value,
                    eachFontMaster.name,
                    firstName,
                    secondName,
                    existingValue,
                )

    # remove too-small pairs
    for firstName, secondName, existingValue in to_be_removed:
        font.removeKerningForPair(eachFontMasterId, firstName, secondName)
        printString += "0\t%s: %s, %s, %s\n" % (
            eachFontMaster.name,
            firstName,
            secondName,
            existingValue,
        )

print(printString)