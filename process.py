from io import BytesIO
import audio2midi

def getFileAndConvertMIDI(file_upload, output_file_name):
    return audio2midi.run(file_upload, output_file_name)
    