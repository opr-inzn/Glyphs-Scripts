# MenuTitle: Round Kerning to 5
# -*- coding: utf-8 -*-

__doc__ = """
Rounds all kerning values to units of 5.
Kerning pairs smaller than the chosen minimum absolute value are deleted.
Cleans broken pairs. Updated and fixed for Glyphs 3.
"""

from GlyphsApp import Glyphs
from vanilla import Window, TextBox, EditText, Button
from AppKit import NSAlert

ROUND_BASE = 5  # Round kerning to nearest 5 units


def alert(text, title="Round Kerning"):
    """Show a blocking alert."""
    a = NSAlert.alloc().init()
    a.setMessageText_(title)
    a.setInformativeText_(text)
    a.runModal()


def myround(x, base=5):
    return int(base * round(float(x) / base))


class RoundKerningDialog:
    def __init__(self):
        self.w = Window((300, 100), "Round Kerning to 5")

        self.w.text = TextBox((15, 12, -15, 20), "Remove pairs smaller than:")
        self.w.minValue = EditText((200, 10, -15, 22), "2")

        self.w.runButton = Button(
            (15, 60, -15, 30), "Round Kerning", callback=self.roundKerning
        )

        self.w.open()
        self.w.makeKey()

    def roundKerning(self, sender):
        # validate input
        try:
            minValue = int(self.w.minValue.get())
        except ValueError:
            alert("Please enter a valid integer.")
            return

        font = Glyphs.font
        if not font:
            alert("No font open.")
            return

        printString = ""
        totalChanges = 0
        totalRemoved = 0

        for master in font.masters:
            mid = master.id
            toRemove = []

            kerningDict = font.kerning.get(mid, {})

            for leftKey, rightDict in dict(kerningDict).items():

                # ----- Resolve left side -----
                if isinstance(leftKey, str):  # class or glyph name
                    if leftKey.startswith("@"):
                        leftOK = True
                        leftName = leftKey
                    else:
                        leftOK = font.glyphs[leftKey] is not None
                        leftName = leftKey
                else:  # glyph ID
                    g = font.glyphForId_(leftKey)
                    leftOK = g is not None
                    leftName = g.name if g else f"[missing:{leftKey}]"

                for rightKey, value in dict(rightDict).items():

                    # ----- Resolve right side -----
                    if isinstance(rightKey, str):
                        if rightKey.startswith("@"):
                            rightOK = True
                            rightName = rightKey
                        else:
                            rightOK = font.glyphs[rightKey] is not None
                            rightName = rightKey
                    else:
                        g = font.glyphForId_(rightKey)
                        rightOK = g is not None
                        rightName = g.name if g else f"[missing:{rightKey}]"

                    # ----- Remove broken pairs -----
                    if not (leftOK and rightOK):
                        toRemove.append((leftKey, rightKey, value))
                        continue

                    # ----- Remove small values -----
                    if abs(value) < minValue:
                        toRemove.append((leftKey, rightKey, value))
                        continue

                    # ----- Round + apply -----
                    newValue = myround(value, ROUND_BASE)
                    if newValue != value:
                        try:
                            font.setKerningForPair(mid, leftKey, rightKey, newValue)
                            printString += f"{newValue}\t{master.name}: {leftName}, {rightName}  (was {value})\n"
                            totalChanges += 1
                        except KeyError:
                            # Catch leftover UUID kerning
                            toRemove.append((leftKey, rightKey, value))
                            continue

            # ----- Remove all scheduled pairs -----
            for leftKey, rightKey, oldValue in toRemove:
                try:
                    font.removeKerningForPair(mid, leftKey, rightKey)
                    totalRemoved += 1
                    printString += f"0\t{master.name}: {leftKey}, {rightKey}  (removed {oldValue})\n"
                except Exception:
                    pass

        # Print summary
        if printString:
            print(printString)

        Glyphs.showNotification(
            "Kerning Rounded",
            f"Rounded to {ROUND_BASE}. Removed {totalRemoved} pairs < {minValue}. Adjusted {totalChanges} pairs.",
        )

        self.w.close()


RoundKerningDialog()
