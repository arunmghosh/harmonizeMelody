import json


class Chord:
    def __init__(self, definition, inversion):
        self.symbol = definition["symbol"]
        self.degrees = definition["scaleDegrees"]
        self.next = definition["next"]
        self.inversion = inversion

    def __str__(self):
        if self.inversion == 0:
            return self.getSymbol()
        elif self.inversion == 1:
            return self.getSymbol() + "6"
        else:
            return self.getSymbol() + "64"

    def getDegrees(self):
        return self.degrees

    def getSymbol(self):
        return self.symbol

    def getInversion(self):
        return self.inversion

    def hasScaleDegree(self, note):
        return note in self.degrees

    @classmethod
    def chordFromSymbol(cls, symbol, inversion):
        fileName = symbol + "_info.json"
        with open(fileName, "r") as chord_json:
            definition = json.load(chord_json)
            return cls(definition, inversion)

    def getSuccessors(self, note):
        successors = list()
        for d in self.next:  # d is a dictionary
            for n in ["0", "1", "2"]:
                if n in d["inversions"]:
                    for c in d["inversions"][n]:
                        candidate = Chord.chordFromSymbol(d["symbol"], c)
                        if candidate.hasScaleDegree(note):
                            successors.append(candidate.getSymbol())
        return successors

    def passesChecks(self, note, nextNote, nextChord):
        # check for objectionable parallels
        # check successors of node against nodes listed under the next note in g
        # check for 7th resolutions

        if self.hasParallels(nextChord, note, nextNote):
            return False
        elif nextChord.getSymbol() not in self.getSuccessors(nextNote):
            return False
        else:
            if 7 in self.getDegrees():
                deg = self.getDegrees().index(7)
                if not nextChord.getDegrees()[deg] == 1:
                    return False
                else:
                    return True
            else:
                return True

    def getFollowers(self, note, nextNote):
        followers = dict()
        for d in self.next:  # d is a dictionary
            if self.passesChecks(note, nextNote, Chord.chordFromSymbol(d["symbol"], 0)):
                followers[d["symbol"]] = d["inversions"]
        return followers

    def inFollowers(self, chord, note):  # test if chord is in self.getFollowers()
        if chord.getSymbol() in self.getFollowers(note):
            if str(self.getInversion()) in self.getFollowers(note)[chord.getSymbol()]:
                if chord.getInversion() in self.getFollowers(note)[chord.getSymbol()][str(self.getInversion())]:
                    return True
        return False

    def hasParallels(self, nextChord, note1, note2):
        bassNote1 = self.degrees[self.inversion]
        bassNote2 = nextChord.degrees[nextChord.inversion]
        interval1 = (note1 - bassNote1) % 7
        interval2 = (note2 - bassNote2) % 7
        # need to somehow deal with case where current chord and next chord are identical
        if interval1 == interval2:
            if interval1 == 0:
                return True
            elif interval1 == 4:
                if note1 == 4 or note2 == 4:
                    return False
                else:
                    return True