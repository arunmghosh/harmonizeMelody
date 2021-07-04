from music21 import *


# extract the notes with a function
def get_notes(instrument_type, path):
	try:
		midi = converter.parse(path)
		parts = instrument.partitionByInstrument(midi)
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

def getFirstChord(note, palette):
	options = dict{} #this will be fed to the scoring algorithm when it has been fully populated
	for chord in palette:
		options[chord] = dict{} 
	return options

def getNextChord(note, next_note, chord): #different case than the first chord because more constraints come into play
	#iterates through dictionary and populates the empty dictionaries stored under keys that represent the options for the previous chord
	#the options parameter could be the high-level dictionary defined in getFirstChord or a lower-level dictionary
	#call getSuccessors() and checkForParallels(), each empty dictionary is populated with the successors that pass the parallel check
	choices = dict{}
	for c in chord.getSuccesors(next_note):
		if not chord.hasParallels(c, note, next_note):
			choices[c] = dict{} 
	return choices 

def getChordProgressions(melody, symbols):
	#define palette
	palette = getChordPalette(symbols)
	
	#start by determining which chords can start the progression, as the rules get more strict for the successors
	firstNote = melody[0]
	progressions = getFirstChord(firstNote, palette) #high-level structure, this will be returned (this is a dictionary)
	
	#assign values to keys (nesting dictionaries)		

def main():
	# retrieve MIDI file
	address = r"/Users/arun/Documents/testMelody1.mid"  # file path

	melody = get_notes("Piano",address)


if __name__ == '__main__':
	main()
