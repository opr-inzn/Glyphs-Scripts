# MenuTitle: Round Kerning to 5
# encoding: utf-8

__doc__ = """
Rounds the kerning values to units of 5.
Original script by Wei Huang.
"""

from GlyphsApp import *
from vanilla import *


def myround(x, base=5):
    return int(base * round(float(x) / base))


class RoundKerningDialog(object):
    def __init__(self):
        self.w = Window((300, 100), "Round Kerning to 5")

        self.w.text = TextBox((15, 12, -15, 20), "Remove pairs smaller than:")
        self.w.minValue = EditText(
            (200, 10, -15, 22), "5", sizeStyle="regular"
        )

        self.w.runButton = Button(
            (15, 60, -15, 30), "Round Kerning", callback=self.roundKerning
        )

        self.w.open()
        self.w.makeKey()

    def roundKerning(self, sender):
        try:
            minValue = int(self.w.minValue.get())
        except ValueError:
            Message("Please enter a valid integer for MIN_VALUE.")
            return

        font = Glyphs.font
        printString = ""

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

                    if abs(existingValue) < minValue:
                        to_be_removed.append(
                            (firstName, secondName, existingValue)
                        )
                    elif existingValue != value:
                        font.setKerningForPair(
                            eachFontMasterId, firstName, secondName, value
                        )
                        printString += "%s\t%s: %s, %s, %s\n" % (
                            value,
                            eachFontMaster.name,
                            firstName,
                            secondName,
                            existingValue,
                        )

            # remove too-small pairs
            for firstName, secondName, existingValue in to_be_removed:
                font.removeKerningForPair(
                    eachFontMasterId, firstName, secondName
                )
                printString += "0\t%s: %s, %s, %s\n" % (
                    eachFontMaster.name,
                    firstName,
                    secondName,
                    existingValue,
                )

        print(printString)
        Glyphs.showNotification(
            "Kerning Rounded",
            f"Kerning rounded to 5, pairs smaller than {minValue} removed.",
        )

        # ✅ Close dialog after running
        self.w.close()

RoundKerningDialog()