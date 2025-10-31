import sys
import os
import glob
from music21 import converter

def musicxml_to_midi(xml_filepath):
    """Converts a MusicXML file to a MIDI file using music21."""
    
    if not os.path.exists(xml_filepath):
        print(f"Error: MusicXML file not found at {xml_filepath}")
        return

    # Determine output path: replace .mxl or .xml extension with .mid
    base, ext = os.path.splitext(xml_filepath)
    midi_filepath = base + ".mid"

    print(f"-> Converting {os.path.basename(xml_filepath)} to MIDI...")
    
    try:
        # 1. Parse the MusicXML file into a music21 Score object
        score = converter.parse(xml_filepath)

        # 2. Export the Score object as a MIDI file
        score.write('midi', fp=midi_filepath)

        print(f"   ✅ MIDI saved to: {midi_filepath}")

    except Exception as e:
        print(f"   ❌ An error occurred during conversion: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python xml_to_midi.py <path/to/musicxml_file.mxl>")
        sys.exit(1)
        
    musicxml_to_midi(sys.argv[1])
