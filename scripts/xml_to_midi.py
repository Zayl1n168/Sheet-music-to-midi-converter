import sys
import os
import re
import music21 as m21
import zipfile
import io

def get_xml_string(file_path):
    """Handles both compressed (.mxl) and uncompressed (.xml) files."""
    base_name, ext = os.path.splitext(file_path)
    xml_string = None
    
    try:
        if ext.lower() == '.mxl':
            # It's a compressed MusicXML file (ZIP format)
            with open(file_path, 'rb') as f:
                mxl_bytes = io.BytesIO(f.read())
            
            with zipfile.ZipFile(mxl_bytes, 'r') as z:
                # Prioritize the largest file (which is almost always the music data)
                largest_file_name = None
                largest_file_size = -1
                
                for name in z.namelist():
                    if name.lower().endswith(('.xml', '.musicxml')) and not name.startswith('META-INF'):
                        info = z.getinfo(name)
                        if info.file_size > largest_file_size:
                            largest_file_size = info.file_size
                            largest_file_name = name

                if largest_file_name:
                    # Read the uncompressed XML content using latin-1 encoding for safety
                    xml_string = z.read(largest_file_name).decode('latin-1')
                else:
                    raise ValueError("Could not find the main MusicXML file inside the .mxl archive.")
        
        elif ext.lower() in ('.xml', '.musicxml'):
            # It's a standard uncompressed XML file
            with open(file_path, 'r', encoding='latin-1') as f:
                xml_string = f.read()

    except Exception as e:
        raise IOError(f"Error reading file '{file_path}': {e}")
        
    return xml_string

def convert_xml_to_midi(xml_file_path):
    print(f"-> Converting {os.path.basename(xml_file_path)} to MIDI...")
    
    try:
        # 1. Read the XML content (handles compression and encoding)
        xml_string = get_xml_string(xml_file_path)

        # 2. Clean XML: Remove unbound namespace prefixes (critical fix for Audiveris output)
        xml_string = re.sub(r'<\/?([a-zA-Z0-9]+):', r'<\/?', xml_string)
        xml_string = re.sub(r' ([a-zA-Z0-9]+):([a-zA-Z0-9]+)=', r' \2=', xml_string)
        
        # 3. Parse the cleaned string
        score = m21.converter.parse(xml_string, format='musicxml')

        # 4. Write the MIDI file
        base_dir = os.path.dirname(xml_file_path)
        base_name = os.path.basename(xml_file_path).split('.')[0]
        midi_path = os.path.join(base_dir, f"{base_name}.mid")
        
        score.write('midi', fp=midi_path)
        
        print(f"   ✅ Successfully converted to {midi_path}")
    
    except Exception as e:
        print(f"   ❌ An error occurred during conversion: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        convert_xml_to_midi(sys.argv[1])
    else:
        print("Error: No MusicXML file path provided.")
