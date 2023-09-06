import vosk
import pyaudio
import os
import json
from src.base_logger import logger
from src.english.DictionaryEnglish import load_dictionary

# This chunk of code HAS to be declared in the outer scope because of the get_text_from_audio function
# Otherwise the recognizer and stream parameters remain static, which messes the speech detection up
# Load in the vosk model
file_directory = os.path.dirname(__file__)
model_directory = os.path.join(file_directory, '../Model/vosk-model-small-en-us-0.15')
grammar_words_directory = os.path.join(file_directory, '../text_files/vocabulary_words.txt')

grammar = []
with open(os.path.abspath(grammar_words_directory), encoding='utf8') as _:
    for line in _:
        line = line.strip()
        if line:
            grammar.append(line)


dictionary = load_dictionary()
dict_keys = list(dictionary.keys())

for i in range(len(dictionary)):
    synonyms = dictionary.get(dict_keys[i])[1]

    for j in range(len(synonyms)):
        grammar.append(synonyms[j])

# Word lists that are used for speech detection
confirmation_words = ["yes", "yet", "ya", "ok", "okay", "okey", "yeah", "sure", "correct", "is true",
                      "indeed", "positive"]
denial_words = ["no", "nope", "know", "nah", "incorrect", "is not true", "negative"]
skip_words = ["skip", "don't know", "i don't know", "not sure", "tip", "hint", "clue", "skipped"]

grammar.extend(confirmation_words)
grammar.extend(denial_words)
grammar.extend(skip_words)

json = json.dumps(grammar)

model = vosk.Model(model_directory)
recognizer = vosk.KaldiRecognizer(model, 16000, json)

# Take microphone input
mic = pyaudio.PyAudio()
stream = mic.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=8192)


def get_text_from_audio():
    data = stream.read(4096, exception_on_overflow=False)

    logger.info("SPEECH: listening to user...")

    if recognizer.AcceptWaveform(data):
        return recognizer.Result()


def main():
    text = False
    while not text:

        text = get_text_from_audio()

        if text:
            print(text)


if __name__ == "__main__":
    main()
