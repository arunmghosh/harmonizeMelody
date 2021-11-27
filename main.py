from music21 import *
from Key import Key
from Chord import Chord
import numpy
import json


# extract the notes with a function
def get_notes(instrument_type, path):
    try:
        midi_data = converter.parse(path)
        parts = instrument.partitionByInstrument(midi_data)
        notes = []
        for music_instrument in range(len(parts)):
            if parts.parts[music_instrument].id in instrument_type:
                for element_by_offset in stream.iterator.OffsetIterator(parts[music_instrument]):
                    for entry in element_by_offset:
                        if isinstance(entry, note.Note):
                            notes.append(str(entry.pitch.midi))
                        elif isinstance(entry, note.Rest):
                            notes.append('Rest')
        return notes

    # handle errors (for example, MIDI file could be corrupted)
    except Exception as e:
        print(path, " did not work, please try again")
        pass


def process_notes(notes):
    # remove rests from the notes array
    melody = list()  # stores list of midi pitches that will be returned
    for n in notes:
        if type(n) == int:
            melody.append(n)
    return melody


def get_palette_root(symbols):
    # returns an array of root position chord objects
    palette = numpy.empty(len(symbols), dtype=Chord)
    for i in range(len(symbols)):
        palette.put(i, Chord.chord_from_symbol(symbols[i], 0))
    return palette


def get_chords(degree, palette):
    chords = numpy.empty(3, dtype=Chord)  # we know that only 3 chords will have the degree
    counter = 0  # index in chords where chord obj will be placed
    for c in palette:
        if c.has_scale_degree(degree):
            chords.put(counter, c)
            counter += 1
    return chords


def preprocess(palette):
    # create scale degree definitions
    for deg in range(1, 8):
        definition = dict()
        for next_deg in range(1, 8):
            if not deg == next_deg:
                definition[next_deg] = dict()
                # keys of lower level dictionaries will be symbols
                # of root position chords that can harmonize deg
                for c in range(len(palette)):
                    if palette[c].has_scale_degree(deg):
                        # the get_followers method from the chord class will take care of the rest
                        definition[next_deg][palette[c].get_symbol()] = palette[c].get_followers(deg, next_deg)
        filename = str(deg) + "_info.json"
        json_obj = definition
        with open(filename, "w") as jsonFile:
            json.dump(json_obj, jsonFile)
    return


def check_traversal_status(path_type, upper_bound):
    for i in range(upper_bound):
        if path_type[i] < 2:
            return False
    return True


def is_finished(error_tracker, current_index, symbol_path, inv_path, degrees):
    # check if more possibilities remain
    if error_tracker[0] == 0:  # found a valid progression
        if check_traversal_status(inv_path, len(degrees)):
            return check_traversal_status(symbol_path, len(degrees))
        return False

    if error_tracker[0] == 1:  # current symbol did not work
        return check_traversal_status(symbol_path, current_index[0] + 1)

    if error_tracker[0] == 2:  # prev inv did not work
        if check_traversal_status(inv_path, current_index[0]):
            return check_traversal_status(symbol_path, current_index[0] + 1)
        return False

    if error_tracker[0] == 3:  # prev inv did not work
        if check_traversal_status(inv_path, current_index[0] + 1):
            return check_traversal_status(symbol_path, current_index[0] + 1)
        return False


def trace_path(symbol_path, inv_path, degrees, palette):
    path = numpy.empty(len(degrees), dtype=Chord)
    for i in range(len(path)):
        inv = inv_path[i]
        symbol = get_chords(degrees[i], palette)[symbol_path[i]].get_symbol()
        path.put(i, Chord.chord_from_symbol(symbol, inv))
    return path


def update_path(path_type, upper_bound):
    for i in range(upper_bound - 1, -1, -1):
        if path_type[i] < 2:
            path_type.put(i, path_type[i] + 1)
            for j in range(i + 1, len(path_type)):
                path_type.put(j, 0)
            return i
    return -1


def edit_paths(error_tracker, current_index, symbol_path, inv_path, degrees, palette):
    if error_tracker[0] == 0:  # found a valid progression
        spot = update_path(inv_path, len(degrees))
        if not spot == -1:
            current_index.put(0, spot)
        else:
            new_spot = update_path(symbol_path, len(degrees))
            current_index.put(0, new_spot)

    if error_tracker[0] == 1:  # current symbol did not work
        spot = update_path(symbol_path, current_index[0] + 1)
        current_index.put(0, spot)

    if error_tracker[0] == 2:  # prev inv did not work
        spot = update_path(inv_path, current_index[0])
        if not spot == -1:
            current_index.put(0, spot)
        else:
            new_spot = update_path(symbol_path, current_index[0] + 1)
            for k in range(len(inv_path)):
                inv_path.put(k, 0)
            current_index.put(0, new_spot)

    if error_tracker[0] == 3:  # current inv did not work
        spot = update_path(inv_path, current_index[0] + 1)
        if not spot == -1:
            current_index.put(0, spot)
        else:
            new_spot = update_path(symbol_path, current_index[0] + 1)
            for k in range(len(inv_path)):
                inv_path.put(k, 0)
            current_index.put(0, new_spot)

    trace_path(symbol_path, inv_path, degrees, palette)


def get_progressions(degrees, palette):
    structure = numpy.empty(len(degrees) - 1, dtype=dict)
    for n in range(len(degrees) - 1):
        file_name = str(degrees[n]) + "_info.json"
        with open(file_name, "r") as data:
            degree_def = json.load(data)
            relevant_data = degree_def[str(degrees[n+1])]
            structure.put(n, relevant_data)
    print(structure)
    symbol_path = numpy.zeros(len(degrees), dtype=int)
    inv_path = numpy.zeros(len(degrees), dtype=int)
    progressions = traverse(structure, degrees, palette, symbol_path, inv_path)
    return progressions


def traverse(structure, degrees, palette, symbol_path, inv_path):
    progressions = list()  # will be returned once populated
    error_tracker = numpy.empty(1, dtype=int)
    current_index = numpy.empty(1, dtype=int)
    current_index.put(0, 0)
    finished = False

    while not finished:
        # check if we are finished (base case)
        candidate = depth_first(structure, symbol_path, inv_path, current_index, degrees, palette, error_tracker)

        if candidate is not None:  # found a valid progression
            progressions.append(candidate)

        finished = is_finished(error_tracker, current_index, symbol_path, inv_path, degrees)

        if not finished:  # need to edit the paths and set current index for next call of depth first
            edit_paths(error_tracker, current_index, symbol_path, inv_path, degrees, palette)

    return progressions


def depth_first(structure, symbol_path, inv_path, current_index, degrees, palette, error_tracker):
    # start with base case
    if current_index[0] > len(structure):  # inv_path, symbol_path, and path have length len(degrees)
        error_tracker.put(0, 0)  # no error
        print(symbol_path, inv_path)
        print("valid progression, error state is 0")
        return trace_path(symbol_path, inv_path, degrees, palette)

    # if current index is 0, we can't look backward so this must be a separate case
    if current_index[0] == 0:
        current_index.put(0, 1)
        return depth_first(structure, symbol_path, inv_path, current_index, degrees, palette, error_tracker)
    else:
        prev_chord = get_chords(degrees[current_index[0] - 1], palette)[symbol_path[current_index[0] - 1]]
        prev_inv = inv_path[current_index[0] - 1]
        current_chord = get_chords(degrees[current_index[0]], palette)[symbol_path[current_index[0]]]
        current_inv = inv_path[current_index[0]]

        # check to see if the current symbol and inv combo works
        data = structure[current_index[0] - 1][prev_chord.get_symbol()]
        try:
            inv_data = data[current_chord.get_symbol()]
            try:
                current_inv_options = inv_data[str(prev_inv)]
                if current_inv in current_inv_options:
                    current_index.put(0, current_index[0] + 1)
                    return depth_first(structure, symbol_path, inv_path, current_index, degrees, palette, error_tracker)
                else:
                    error_tracker.put(0, 3)  # current inversion didn't work
                    print(symbol_path, inv_path)
                    print("current inversion failed, error state is 3")
                    return None
            except KeyError:
                error_tracker.put(0, 2)  # previous inversion didn't work
                print(symbol_path, inv_path)
                print("previous inversion failed, error state is 2")
                return None
        except KeyError:
            error_tracker.put(0, 1)  # current symbol didn't work
            print(symbol_path, inv_path)
            print("current symbol failed, error state is 1")
            return None


def main():
    # retrieve MIDI file
    # address = r"/Users/arun/Documents/testMelody1.mid"  # file path

    # extracted = get_notes("Piano", address)
    # extracted = [67, 74, 64, "Rest", 72, 67, 71, "Rest", 64, 72, "Rest", "Rest"]
    extracted = [67, 74]
    melody = process_notes(extracted)

    key_symbol = input("What is the key of this melody?: ")
    k = Key.key_from_user(key_symbol)

    degrees = numpy.empty(len(melody), dtype=int)
    for i in range(len(melody)):
        degrees.put(i, k.midi_to_degree(melody[i]))

    print(degrees)
    symbols = ["I", "ii", "iii", "IV", "V", "vi", "viio"]
    palette = get_palette_root(symbols)
    preprocess(palette)

    total = 0
    for p in get_progressions(degrees, palette):
        total += 1
        for c in p:
            print(c)
    print(total)


if __name__ == "__main__":
    main()
