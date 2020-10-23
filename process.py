import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import wave
import sys
from io import BytesIO
from reportlab.platypus import SimpleDocTemplate, Image
from reportlab.lib.utils import ImageReader

from audio_to_midi import audio2midi

def getFileAndConvertPDF(file_upload):
    spf = wave.open(file_upload, "r")
    # Extract Raw Audio from Wav File
    signal = spf.readframes(-1)
    signal = np.fromstring(signal, "Int16")

    f = plt.figure()

    plt.figure(1)
    plt.title("Signal Wave...")
    plt.plot(signal)
    imgdata = BytesIO()
    f.savefig(imgdata, format='png')
    imgdata.seek(0)
    image = ImageReader(imgdata)

    parts = []
    parts.append(Image(imgdata))

    pdf_buffer = BytesIO()
    my_doc = SimpleDocTemplate(pdf_buffer)

    my_doc.build(parts)
    pdf_value = pdf_buffer.getvalue()
    pdf_buffer.seek(0)
    return pdf_buffer

def getFileAndConvertMIDI(file_upload, output_file_name):
    return audio2midi.run(file_upload, output_file_name)
    