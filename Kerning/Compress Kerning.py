# MenuTitle: Compress Kerning
# -*- coding: utf-8 -*-
__doc__ = """
Reduces the number of different kerning values in the current Glyphs file,
similar to a GIF/PNG-8 palette. This is lossy but nearly imperceptible,
and helps reduce webfont size. 
Original script by Just Another Foundry for fontTools.
"""

from GlyphsApp import *

def isValidKerningKey(font, key):
    """Check if kerning key is valid (glyph name or group)."""
    if key is None:
        return False
    if key.startswith("@"):  # kerning group
        return True
    if font.glyphs[key]:  # glyph name exists
        return True
    return False


def collectKerningValues(font):
    """Collect all kerning values from the font."""
    values = []
    pairs = []
    for master in font.masters:
        kerningDict = font.kerning[master.id]
        if not kerningDict:
            continue
        for left, rightDict in kerningDict.items():
            if not rightDict:
                continue
            for right, value in rightDict.items():
                if value is not None:
                    values.append(value)
                    pairs.append((master.id, left, right, value))
    return values, pairs


def palettize_kerning(font, max_tweak_relative=0.003):
    upm = font.upm
    max_tweak = max_tweak_relative * upm
    if max_tweak < 1:
        return

    # Collect values before
    beforeValues, beforePairs = collectKerningValues(font)
    beforeUnique = len(set(beforeValues))

    # Collect all kerning values for processing
    allValueRecords = []  # store (masterID, left, right, value)
    for master in font.masters:
        kerningDict = font.kerning[master.id]
        if not kerningDict:
            continue
        for left, rightDict in kerningDict.items():
            if not rightDict:
                continue
            for right, value in rightDict.items():
                if value is not None:
                    if abs(value) > max_tweak:
                        allValueRecords.append((master.id, left, right, value))
                    else:
                        # too small, set to zero if valid
                        if isValidKerningKey(font, left) and isValidKerningKey(
                            font, right
                        ):
                            font.setKerningForPair(master.id, left, right, 0)

    if not allValueRecords:
        print("⚠️ No kerning values found to process.")
        return

    # Create sorted unique list of all kerning values
    allValues = sorted({v for (_, _, _, v) in allValueRecords})

    # Set up spans
    spans = []
    max_span = int(round(2.0 * max_tweak + 1))
    lower = allValues[0]
    for v in allValues:
        if v < lower + max_span:
            upper = v
        else:
            spans.append([int(lower), int(upper)])
            lower = v
            upper = v
    spans.append([int(lower), int(upper)])

    # Equalize adjacent spans
    for i in range(len(spans) - 1):
        middle = (spans[i][0] + spans[i + 1][1]) // 2
        if spans[i][1] > middle:
            spans[i][1] = middle
            while spans[i][1] > spans[i][0] and spans[i][1] not in allValues:
                spans[i][1] -= 1
            spans[i + 1][0] = middle + 1
            while (
                spans[i + 1][0] < spans[i + 1][1]
                and spans[i + 1][0] not in allValues
            ):
                spans[i + 1][0] += 1
        else:
            assert spans[i + 1][0] >= middle + 1

    # Build mapping
    mapping = {}
    for span in spans:
        middle = int(0.5 * (span[0] + span[1]))
        for i in range(span[0], span[1] + 1):
            mapping[i] = middle

    # Apply mapping
    changed = 0
    for (masterID, left, right, value) in allValueRecords:
        if value in mapping:
            if isValidKerningKey(font, left) and isValidKerningKey(font, right):
                newValue = mapping[value]
                if newValue != value:
                    changed += 1
                font.setKerningForPair(masterID, left, right, newValue)

    # Collect values after
    afterValues, afterPairs = collectKerningValues(font)
    afterUnique = len(set(afterValues))

    # Estimate size savings (rough: assume ~6 bytes per pair + 2 per unique value)
    beforeSize = len(beforePairs) * 6 + beforeUnique * 2
    afterSize = len(afterPairs) * 6 + afterUnique * 2
    savings = beforeSize - afterSize
    percent = (savings / beforeSize * 100) if beforeSize > 0 else 0

    # Report
    print("✅ Palettize Kerning Report")
    print(f"  Kerning pairs processed: {len(beforePairs)}")
    print(f"  Unique values before: {beforeUnique}")
    print(f"  Unique values after:  {afterUnique}")
    print(f"  Changed pairs: {changed}")
    print(f"  Estimated GPOS size before: {beforeSize} bytes")
    print(f"  Estimated GPOS size after:  {afterSize} bytes")
    print(f"  Estimated savings: {savings} bytes ({percent:.1f}%)")


# Run on current font
font = Glyphs.font
if font:
    font.disableUpdateInterface()
    palettize_kerning(font)
    font.enableUpdateInterface()