import vosk
import pyaudio
import os

# This chunk of code HAS to be declared in the outer scope because of the get_text_from_audio function
# Otherwise the recognizer and stream parameters remain static, which messes the speech detection up
# Load in the vosk model
model = vosk.Model(os.path.abspath("vosk-model-small-en-us-0.15"))
recognizer = vosk.KaldiRecognizer(model, 16000)

# Take microphone input
mic = pyaudio.PyAudio()
stream = mic.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=8192)


def get_text_from_audio():
    data = stream.read(4096, exception_on_overflow=False)

    if recognizer.AcceptWaveform(data):
        return recognizer.Result()[14:-3]
