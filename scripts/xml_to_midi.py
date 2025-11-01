import sys
import os
import re
import music21 as m21

def convert_xml_to_midi(xml_file_path):
    # 1. Read the raw file content
    try:
        # FIX: Changed encoding to 'latin-1' to handle non-UTF-8 bytes written by Audiveris.
        with open(xml_file_path, 'r', encoding='latin-1') as f:
            xml_string = f.read()
    except Exception as e:
        print(f"   ❌ Error reading XML file: {e}")
        return

    # 2. Clean XML: Remove unbound namespace prefixes (e.g., 'scl:', 'xlink:')
    # This addresses the previous "unbound prefix" error.
    
    # Remove prefix from element tags (e.g., <scl:tag -> <tag)
    xml_string = re.sub(r'<\/?([a-zA-Z0-9]+):', r'<\/?', xml_string)
    
    # Remove prefix from attributes (e.g., scl:attribute="val" -> attribute="val")
    xml_string = re.sub(r' ([a-zA-Z0-9]+):([a-zA-Z0-9]+)=', r' \2=', xml_string)
    
    try:
        # 3. Parse the cleaned string directly with music21
        score = m21.converter.parse(xml_string, format='musicxml')

        # 4. Write the MIDI file
        base_dir = os.path.dirname(xml_file_path)
        base_name = os.path.basename(xml_file_path).replace(".mxl", "")
        midi_path = os.path.join(base_dir, f"{base_name}.mid")
        
        score.write('midi', fp=midi_path)
        
        print(f"   ✅ Successfully converted to {midi_path}")
    
    except Exception as e:
        # If it fails here, the core musical structure is likely invalid.
        print(f"   ❌ An error occurred during conversion: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        print(f"-> Converting {os.path.basename(sys.argv[1])} to MIDI...")
        convert_xml_to_midi(sys.argv[1])
    else:
        print("Error: No MusicXML file path provided.")
