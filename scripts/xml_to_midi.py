import zipfile
import io
import os
import re
import music21 as m21

# --- Helper Function: Extracts XML from .mxl or reads .xml directly ---
def get_xml_string(file_path):
    """
    Reads the content of a MusicXML file. Handles both compressed (.mxl)
    and uncompressed (.xml) files.
    """
    if file_path.lower().endswith('.mxl'):
        # 1. Handle compressed .mxl file (which is a ZIP archive)
        with open(file_path, 'rb') as f:
            mxl_bytes = io.BytesIO(f.read())
        
        with zipfile.ZipFile(mxl_bytes, 'r') as z:
            largest_file_name = None
            largest_file_size = -1
            
            # Find the main XML file (usually the largest one, ignoring META-INF)
            for name in z.namelist():
                if name.lower().endswith('.xml') and not name.startswith('META-INF'):
                    info = z.getinfo(name)
                    if info.file_size > largest_file_size:
                        largest_file_size = info.file_size
                        largest_file_name = name

            if largest_file_name:
                return z.read(largest_file_name).decode('utf-8')
            else:
                raise ValueError("No main MusicXML file found in the archive.")
    
    elif file_path.lower().endswith('.xml'):
        # 2. Handle uncompressed .xml file
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
            
    else:
        raise ValueError("File must be a MusicXML (.mxl or .xml) file.")

# --- Main Conversion Function ---
def convert_xml_to_midi(xml_file_path):
    print(f"-> Converting {os.path.basename(xml_file_path)} to MIDI...")
    
    try:
        # 1. Read the XML content (extracts from .mxl or reads .xml)
        xml_string = get_xml_string(xml_file_path)

        # 2. Clean XML: Remove unbound namespace prefixes (critical fix for Audiveris output)
        # This prevents music21 errors from poorly formed XML
        xml_string = re.sub(r'<\/?([a-zA-Z0-9]+):', r'<\/?', xml_string)
        xml_string = re.sub(r' ([a-zA-Z0-9]+):([a-zA-Z0-9]+)=', r' \2=', xml_string)
        
        base_dir = os.path.dirname(xml_file_path)
        base_name = os.path.basename(xml_file_path).split('.')[0]
        
        # 3. WRITE THE UNCOMPRESSED .XML FILE TO DISK (NEW STEP)
        xml_path = os.path.join(base_dir, f"{base_name}.xml")
        with open(xml_path, 'w', encoding='utf-8') as xml_file:
            xml_file.write(xml_string)
        print(f"   ✅ Saved uncompressed XML to {xml_path}")
        
        # 4. Parse the cleaned string and convert to MIDI
        score = m21.converter.parse(xml_string, format='musicxml')

        # 5. Write the MIDI file
        midi_path = os.path.join(base_dir, f"{base_name}.mid")
        score.write('midi', fp=midi_path)
        
        print(f"   ✅ Successfully converted to {midi_path}")
    
    except Exception as e:
        print(f"   ❌ An error occurred during conversion: {e}")

# --- Execution Block ---
if __name__ == '__main__':
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python xml_to_midi.py <path_to_musicxml_file>")
        sys.exit(1)
        
    for file_path in sys.argv[1:]:
        convert_xml_to_midi(file_path)
