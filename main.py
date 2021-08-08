from music21 import *
from Chord import Chord
from Key import Key
import numpy
import json


# extract the notes with a function
def get_notes(instrument_type, path):
    try:
        midiData = converter.parse(path)
        parts = instrument.partitionByInstrument(midiData)
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


def getChordPalette(symbols):
    chords = list()
    for s in symbols:
        chords.append(Chord.chordFromSymbol(s, 0))
        chords.append(Chord.chordFromSymbol(s, 1))
        chords.append(Chord.chordFromSymbol(s, 2))
    return chords


def getChordPaletteRoot(symbols):
    chords = list()
    for s in symbols:
        chords.append(Chord.chordFromSymbol(s, 0))
    return chords


def getChordChoices(n, palette):
    choices = list()
    for c in palette:
        if c.hasScaleDegree(n):
            choices.append(c)
    return choices


def createNode(c, n, place, id):  # will implement IDs soon
    # chord, melodic note, and places it occurs in the progression
    places = list()  # list of indices, so the 1st note is represented by 0
    places.append(place)
    info = dict({"chord": c, "note": n, "places": places, "ID": id})
    return info


def updateNode(node, otherPlace):  # node is a dictionary
    node["places"].append(otherPlace)
    return


def getNodeFromID(id, nodes):  # node from ID
    for n in nodes:
        if n["ID"] == id:
            return n
    print("node not found")  # this is for debugging only, will remove later
    return


def getNode(nt, nodes):  # node from note and inversion
    for n in nodes:
        if n["note"] == nt:
            return n
    print("node not found")  # this is for debugging only, will remove later
    return


def isUnique(nt, melody, counter):
    for n in range(0, counter):
        if melody[n] == nt:
            return False
    return True


def getNodes(melody, palette):
    nodes = list()
    counter = 0
    noteCounter = 10
    for n in melody:
        idCounter = 0
        if isUnique(n, melody, counter):
            chords = getChordChoices(n, palette)
            for c in chords:
                nodes.append(createNode(c, n, counter, idCounter+noteCounter))
                idCounter += 1
        else:
            otherPlace = melody.index(n, 0, counter)
            for nd in searchNodes(otherPlace, nodes)[0]:
                updateNode(nd, counter)
        counter += 1
        noteCounter += 10

    return nodes


def midiToScaleDegrees(midiNumbers, k):
    degrees = list()
    for n in midiNumbers:
        degrees.append(k.getScaleDegree(n))
    return degrees


def searchNodes(place, nodes):
    validNodes = numpy.empty(shape=[1, 9], dtype=dict)
    counter = 0
    for n in nodes:
        if place < len(n["places"]):  # prevents index error
            for p in range(place+1):  # only searches first index if 0 is place
                if n["places"][p] == place:
                    validNodes.put(counter, n)
                    counter += 1
        else:
            for p in n["places"]:
                if p == place:
                    validNodes.put(counter, n)
                    counter += 1
    return validNodes


def passesChecks(chord, nextChord, note, nextNote):
    # check for objectionable parallels
    # check successors of node against nodes listed under the next note in g
    # check for 7th resolutions

    if chord.hasParallels(nextChord, note, nextNote):
        return False
    elif nextChord.getSymbol() not in chord.getSuccessors(nextNote):
        return False
    else:
        if 7 in chord.getDegrees():
            deg = chord.getDegrees().index(7)
            if not nextChord.getDegrees()[deg] == 1:
                return False
            else:
                return True
        else:
            return True


def pathToProgression(d, path):
    progression = numpy.empty(len(path), dtype=Chord)
    for spot in range(len(path)):
        progression.put(spot, d[spot][0][path[spot] - 1]["chord"].__str__())
    return progression


def depthFirstTwo(d, currentIndex, path):
    # d is a dictionary mapping melodic notes to nodes
    # currentIndex tells the program what note it's on
    # path traces the progression

    # check to see if progression is finished
    if currentIndex > len(path):
        return pathToProgression(d, path)

    # update path since we know there will not be a bounds error, and define necessary parameters for transition check
    path.put(currentIndex - 1, path[currentIndex - 1] + 1)
    startNode = d[currentIndex - 2][0][path[currentIndex - 2] - 1]  # node that was just added
    nextNode = d[currentIndex - 1][0][path[currentIndex - 1] - 1]  # node that we are considering adding

    # check if transition is invalid, which will end the pass
    if not passesChecks(startNode["chord"], nextNode["chord"], startNode["note"], nextNode["note"]):
        return None

    # transition passed, so move onto the next index and make recursive call
    currentIndex += 1
    return depthFirstTwo(d, currentIndex, path)


def traverse(d, path, progressions):  # calls depthFirstTwo until all possible progressions have been found
    finished = False
    started = False
    while not finished:
        nextPassIndex = -1  # determine where to start the next progression
        for i in range(1, len(path) + 1):
            if 0 < path[i - 1] < 9:
                nextPassIndex = i
        if nextPassIndex < 0:  # traversal is complete
            finished = True
        else:
            if nextPassIndex == 1:  # reset first element of path
                pointer = 2  # tells us where we are in the progression, 2 means second note
                if started:
                    path.put(0, path[0] + 1)  # updating choice for first node
            else:
                pointer = nextPassIndex
            for i in range(nextPassIndex + 1, len(path) + 1):  # all successors need to be 0
                path.put(i - 1, 0)
            candidate = depthFirstTwo(d, pointer, path)
            if candidate is not None:
                progressions.append(candidate)
        started = True
    print(progressions)
    return


def getProgressionsTwo(melody, nodes):
    # create dictionary of indices in the melody
    structure = dict()
    for n in range(len(melody)):
        structure[n] = searchNodes(n, nodes)  # call method to search nodes

    path = numpy.zeros((len(melody),), dtype=int)
    path.put(0, 1)
    progressions = list()

    # traverse structure using a depth-first approach
    # method only finds one progression at a time to avoid recursion error
    traverse(structure, path, progressions)
    print(len(progressions))
    return


def preprocess(deg, palette):
    data = dict()
    for i in range(1, 8):
        if not deg == i:
            data[i] = dict()
            for c in getChordChoices(deg, palette):
                data[i][c.getSymbol()] = c.getFollowers(deg, i)
    print(data)
    filename = str(deg) + "_info.json"
    json_obj = data
    with open(filename, "w") as jsonFile:
        json.dump(json_obj, jsonFile)
    return


def makeProg(path):
    prog = numpy.empty(len(path), dtype= Chord)
    i = 0
    for c in path:
        prog.put(i, Chord.chordFromSymbol(c.getSymbol(), c.getInversion()))
        i += 1
    return prog


def depthFirstProcessed(d, melody, palette, currentIndex, path, symbolPath, invPath, recursiveCall, change):
    if currentIndex == len(path):
        change.put(0, 1)
        print(symbolPath, invPath, "Success")
        return makeProg(path)

    if recursiveCall:
        if symbolPath[currentIndex] == 0:
            symbolPath.put(currentIndex, 1)
        if invPath[currentIndex] == 0:
            invPath.put(currentIndex, 1)

    symbolCounter = symbolPath[currentIndex] - 1
    invCounter = invPath[currentIndex] - 1
    currentNote = melody[currentIndex]
    currentSymbol = getChordChoices(currentNote, palette)[symbolCounter].getSymbol()  # get symbol option

    if currentIndex == 0:
        currentInv = invCounter  # get inversion option
        path.put(0, Chord.chordFromSymbol(currentSymbol, currentInv))  # add it to path at index 0
        print(symbolPath, invPath)
        return depthFirstProcessed(d, melody, palette, currentIndex + 1, path, symbolPath, invPath, True, change)
    else:
        prevNote = melody[currentIndex - 1]
        prevSymbol = path[currentIndex - 1].getSymbol()
        prevInv = path[currentIndex - 1].getInversion()
        try:
            chord = d[prevNote][str(currentNote)][prevSymbol][currentSymbol]
            try:
                options = chord[str(prevInv)]
                try:
                    currentInv = options[invCounter]
                    path.put(currentIndex, Chord.chordFromSymbol(currentSymbol, currentInv))
                    print(symbolPath, invPath)
                    return depthFirstProcessed(d, melody, palette, currentIndex + 1, path, symbolPath, invPath, True, change)
                except IndexError:
                    change.put(0, 2)
                    print(symbolPath, invPath, "Fail")
                    return currentIndex  # signals to traversal method that the invPath needs to be incremented
            except KeyError:
                change.put(0, 2)
                print(symbolPath, invPath, "Fail")
                return currentIndex  # signals to traversal method that the symbolPath needs to be updated
        except KeyError:
            change.put(0, 3)
            print(symbolPath, invPath, "Fail")
            return currentIndex  # signals to traversal method that the symbolPath needs to be updated


def edit_paths(path, symbolPath, invPath, pointer, changePointer):
    if pointer == 0:
        if invPath[0] < 3:
            invPath.put(0, invPath[0] + 1)
        else:
            symbolPath.put(0, symbolPath[0] + 1)
            invPath.put(0, 1)
            for j in range(pointer + 1, len(symbolPath)):  # all successors need to be 1
                symbolPath.put(j, 1)
    else:
        if invPath[pointer] < 3:  # check current chord inversion
            invPath.put(pointer, invPath[pointer] + 1)
        else:
            invPath.put(pointer, 1)
            if invPath[pointer - 1] < 3:  # check previous chord inversion
                invPath.put(pointer - 1, invPath[pointer - 1] + 1)
                path.put(pointer - 1, Chord.chordFromSymbol(path[pointer - 1].getSymbol(), invPath[pointer - 1] - 1))
            else:
                invPath.put(pointer - 1, 1)
                path.put(pointer - 1, Chord.chordFromSymbol(path[pointer - 1].getSymbol(), 0))
                symbolPath.put(pointer, symbolPath[pointer] + 1)  # already know this will not exceed 3
                for j in range(pointer + 1, len(symbolPath)):  # all successors need to be 1
                    symbolPath.put(j, 1)
            if pointer > 1:
                changePointer.put(0, True)
    for k in range(pointer + 1, len(invPath)):  # all successors need to be 1
        invPath.put(k, 1)


def traverseProcessed(d, melody, progressions, palette, path, symbolPath, invPath):
    started = False
    finished = False
    change = numpy.zeros((1,), dtype=int)
    changePointer = numpy.empty(1, dtype=bool)
    pointer = 0
    while not finished:
        # check if we have searched d completely
        if started:
            finished = True

        if change[0] == 1:  # if the previous search did not produce an error and we are done, all values should be 3
            for i in range(len(path) - 1, -1, -1):  # traverse backwards and break if condition is met
                if not (symbolPath[i] >= 3 and invPath[i] >= 3):  # can increment
                    finished = False
                    pointer = i
                    break
            if not finished:
                edit_paths(path, symbolPath, invPath, pointer, changePointer)

        elif change[0] == 2:  # if the previous search had an IndexError or KeyError when using inversion
            invPath.put(pointer, 3)  # will not trigger a false break
            for i in range(pointer, -1, -1):  # traverse backwards and break if condition is met
                if not (symbolPath[i] >= 3 and invPath[i] >= 3):  # can increment
                    finished = False
                    pointer = i
                    break
            if not finished:
                edit_paths(path, symbolPath, invPath, pointer, changePointer)

        elif change[0] == 3:  # if the previous search had a KeyError when using symbol
            invPath.put(pointer - 1, 3)  # will not trigger a false break
            invPath.put(pointer, 3)  # will not trigger a false break
            for i in range(pointer, -1, -1):  # traverse backwards and break if condition is met
                if not (symbolPath[i] >= 3 and invPath[i] >= 3):  # can increment
                    finished = False
                    pointer = i
                    break
            if not finished:
                edit_paths(path, symbolPath, invPath, pointer, changePointer)

        if changePointer and not change[0] == 0:
            pointer -= 1

        if not finished or not started:  # call the depthFirstProcessed method
            started = True
            change.put(0, 0)
            changePointer.put(0, False)
            candidate = depthFirstProcessed(d, melody, palette, pointer, path, symbolPath, invPath, False, change)
            if not type(candidate) == int:
                progressions.append(candidate)
            else:
                pointer = candidate


def getProgressionsProcessed(melody, palette):
    structure = dict()
    for n in range(1, 8):  # read .json files to get preprocessed data
        fileName = str(n) + "_info.json"
        with open(fileName, "r") as data:
            structure[n] = json.load(data)  # top level keys of dictionary are scale degrees
            # value is data for that scale degree

    path = numpy.empty((len(melody),), dtype=Chord)  # path will store progression until it is finished
    symbolPath = numpy.zeros((len(melody),), dtype=int)
    symbolPath.put(0, 1)
    invPath = numpy.zeros((len(melody),), dtype=int)
    invPath.put(0, 1)
    progressions = list()

    # traverse structure using a depth-first approach
    # method only finds one progression at a time to avoid recursion error
    traverseProcessed(structure, melody, progressions, palette, path, symbolPath, invPath)
    print(len(progressions))
    for p in progressions:
        for c in p:
            print(c)


def main():
    # retrieve MIDI file
    # address = r"/Users/arun/Documents/testMelody1.mid"  # file path

    # melody = get_notes("Piano", address)
    keySymbol = input("What is the key of this melody?: ")
    k = Key.keyFromUser(keySymbol)
    # degrees = midiToScaleDegrees(melody, k)
    degrees = [1, 5, 6, 4, 5, 3, 6, 4]

    # use degrees to generate the nodes
    if k.usesMajorPalette():
        romanNumerals = ["I", "ii", "iii", "IV", "V", "vi", "viio"]
    else:
        romanNumerals = ["i", "iio", "III", "iv", "v", "VI", "VII"]
    chordPalette = getChordPalette(romanNumerals)
    chordPaletteRoot = getChordPaletteRoot(romanNumerals)
    nodes = getNodes(degrees, chordPalette)
    # this will be passed to scoring algorithm
    # getProgressionsTwo(degrees, nodes)
    # preprocess(7, chordPalette)
    getProgressionsProcessed(degrees, chordPaletteRoot)


if __name__ == '__main__':
    main()
