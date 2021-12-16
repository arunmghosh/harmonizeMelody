import numpy
class Grader:
    def __init__(self, progressions):
        self.progressions = progressions
        self.scores = numpy.zeros(len(progressions),dtype=int)

    @staticmethod
    def unique(p):
        # returns the list of unique chords in the progression
        found = list()
        for c in range(len(p)):
            if not p[c] in found:
                found.append(p[c])
        return found

    def check_repeats(self, p):
        # p is any given progression
        repeats_score = 0
        clock = 0  # repeat counter; if the same chord is used more than once in a 4-chord progression
        #                            the progression is marked down
        searching = 0  # index of the chord we are currently checking for repeats of
        to_search = self.unique(p)
        for i in range(len(to_search)):
            # searching starts out at 0
            current_chord = to_search[searching]
            for c in range(len(p)):
                if p[c] == current_chord:
                    clock += 1
                else:
                    clock = 0
                if clock >= 4:
                    repeats_score -= 1
            searching += 1
        return repeats_score

    @staticmethod
    def check_cadences(p):
        first_chord = p[-2]
        second_chord = p[-1]
        if second_chord.get_inversion() == 0:
            if first_chord.get_symbol() == "V":  # authentic or deceptive cadence
                return 0
            if second_chord.get_symbol() == "V":  # half cadence
                return 0
            if first_chord.get_symbol() == "IV" and second_chord.get_symbol() == "I":  # plagal cadence
                return 0
        return -4

    @staticmethod
    def check_64(p):
        second_inv_score = 0
        # need to check for passing, arpeggiated, cadential, pedal
        for i in range(len(p)):
            c = p[i]
            if c.get_inversion() == 2:
                if i == 0 or i == len(p) - 1:
                    second_inv_score -= 1
                else:
                    prev = p[i - 1]
                    next = p[i + 1]
                    prev_note = prev.get_bass_note()
                    current_note = c.get_bass_note()
                    next_note = next.get_bass_note()

                    if not next_note - current_note == current_note - prev_note:
                        # not passing, arrpegiated or pedal
                        if not c.get_symbol() == "I" and next.get_symbol() == "V":
                            # last chord in progression already penalized if inverted,
                            # so we don't need to check that here
                            second_inv_score -= 2
        return second_inv_score

    @staticmethod
    def check_first(p):
        first = p[0]
        if not first.get_inversion() == 0:
            return -3
        return 0

    def grade(self):
        counter = 0  # tracks which index of scores we are updating
        for p in self.progressions:
            # counter will start at 0, and increment in this loop
            s = self.check_first(p) + self.check_64(p) + self.check_cadences(p) + self.check_repeats(p)
            self.scores.put(counter, s)
            counter += 1

    def rank(self):
        top_p = list()  # stores the top-scoring progressions
        top_score = self.scores[0]

        for s in range(len(self.scores)):
            if self.scores[s] > top_score:
                top_p.clear()
                top_p.append(self.progressions[s])
            if self.scores[s] == top_score:
                top_p.append(self.progressions[s])

        return top_p
