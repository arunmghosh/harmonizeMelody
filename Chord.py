import json
import numpy


class Chord:
    def __init__(self, definition, inversion):
        self.symbol = definition["symbol"]
        self.degrees = definition["scaleDegrees"]
        self.next = definition["next"]
        self.inversion = int(inversion)

    def __str__(self):
        macro = self.symbol
        if self.inversion == 0:
            return macro
        if self.inversion == 1:
            return macro + "6"
        if self.inversion == 2:
            return macro + "64"

    def get_symbol(self):
        return self.symbol

    def get_inversion(self):
        return self.inversion

    def get_bass_note(self):
        return self.degrees[self.inversion]

    def get_tenor(self):
        return self.degrees[(self.inversion + 1) % 3]

    def get_alto(self):
        return self.degrees[(self.inversion + 2) % 3]

    @classmethod
    def chord_from_symbol(cls, symbol, inversion):
        file_name = symbol + "_info.json"
        with open(file_name, "r") as chord_json:
            definition = json.load(chord_json)
            return cls(definition, inversion)

    def has_parallels(self, note, next_chord, next_note):
        bass1 = self.get_bass_note()
        bass2 = next_chord.get_bass_note()

        # parallel octaves
        if note == bass1 and next_note == bass2:
            return True

        # parallel fifths
        if note == (bass1 + 4) % 7 and next_note == (bass2 + 4) % 7:
            # 7 to 4 is not a perfect fifth, it is a diminished fifth
            if note == 4 or next_note == 4:
                return False

            # 7 to 4 is not in play so we definitely have parallel fifths
            return True

        return False

    def has_scale_degree(self, degree):
        return degree in self.degrees

    def get_followers(self, note, next_note):
        # precondition: method only invoked on a root position chord
        # eventual return value is a dictionary
        followers = dict()

        # first step is to iterate through self.next to see which chords can harmonize next_note
        for d in self.next:
            symbol = d["symbol"]
            test_chord = Chord.chord_from_symbol(symbol, 0)
            if test_chord.has_scale_degree(next_note):
                followers[symbol] = dict()

                # then iterate through possible inversions of self
                for i in d["inversions"]:
                    followers[symbol][i] = list()

                    # lastly check possible inversions of next_chord and check for parallels
                    for j in d["inversions"][i]:
                        first_chord = Chord.chord_from_symbol(self.get_symbol(), i)
                        second_chord = Chord.chord_from_symbol(symbol, j)
                        if not first_chord.has_parallels(note, second_chord, next_note):
                            followers[symbol][i].append(j)

        return followers
