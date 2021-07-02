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


def main():
	# retrieve MIDI file
	address = r"/Users/arun/Documents/testMelody1.mid"  # file path

	print(get_notes("Piano",address))


if __name__ == '__main__':
	main()