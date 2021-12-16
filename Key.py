class Key:
    def __init__(self, tonic, pattern, to_degrees, to_midi):
        self.tonic = tonic
        self.pattern = pattern
        self.to_degrees = to_degrees
        self.to_midi = to_midi

    @staticmethod
    def get_chromatic_scale_sharps():
        letters = ("C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B",
                   "C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B")
        chromatic_sharps = dict()
        pitch = 0
        for le in letters:
            chromatic_sharps[le] = pitch
            pitch += 1
        return chromatic_sharps

    @staticmethod
    def get_chromatic_scale_flats():
        letters = ("C", "Db", "D", "Eb", "E", "F", "Gb", "G", "Ab", "A", "Bb", "B",
                   "C", "Db", "D", "Eb", "E", "F", "Gb", "G", "Ab", "A", "Bb", "B")
        chromatic_sharps = dict()
        pitch = 0
        for le in letters:
            chromatic_sharps[le] = pitch
            pitch += 1
        return chromatic_sharps

    @classmethod
    def key_from_user(cls, symbol):
        if 'm' not in symbol:
            if 'b' in symbol:
                tonic = cls.get_chromatic_scale_flats()[symbol] % 12
            else:
                tonic = cls.get_chromatic_scale_sharps()[symbol] % 12
            pattern = [2, 2, 1, 2, 2, 2]
            to_degrees = dict()
            to_midi = dict()
            counter = tonic
            for i in range(0, 7):
                to_degrees[counter % 12] = i + 1
                to_midi[i + 1] = counter % 12
                if i < 6:
                    counter += pattern[i]
            return cls(tonic, pattern, to_degrees, to_midi)

    def midi_to_degree(self, midi_pitch):
        return self.to_degrees[midi_pitch % 12]

    def degree_to_midi(self, degree):
        return self.to_midi[degree]
