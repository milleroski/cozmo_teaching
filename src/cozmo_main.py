import cozmo
import vosk
import pyaudio
import json
from Dictionary import load_dictionary


# TODO: Add a lot more logic to this, make the robot ask again, maybe if the user wants to move on to the next word etc.

def get_text_from_audio(stream, recognizer):
    data = stream.read(4096, exception_on_overflow=False)

    if recognizer.AcceptWaveform(data):
        return recognizer.Result()[14:-3]


def get_words(recognizer, stream):
    name = ""
    while not name:
        name = get_text_from_audio(stream, recognizer)
    return name


# Is this function even necessary?
# def check_answer_list(text, word_list):
#     for word in word_list:
#         check_answer(text, word)

def check_answer(text, word):
    text_list = text.split()
    correct_answer = False

    for text_word in text_list:
        if text_word == word.casefold():
            correct_answer = True
            break

    return correct_answer


def cozmo_program(robot: cozmo.robot.Robot):

    # Move Cozmo's head up and the lift down
    robot.move_lift(-3)
    robot.set_head_angle(cozmo.robot.MAX_HEAD_ANGLE).wait_for_completed()  # This doesn't work sometimes?

    # Load in a dictionary, for implementation see Dictionary.py
    dictionary = load_dictionary()
    dict_keys = list(dictionary.keys())
    dict_length = len(dictionary)

    # Vocabulary that the user is likely to use, otherwise vosk will very likely misinterpret it
    confirmation_words =["yes", "no", "yeah", "nope", "sure", "correct"]
    vocabulary = json.dumps(dict_keys + confirmation_words)
    print(vocabulary)

    # Load in the vosk model
    model = vosk.Model(r"Model\vosk-model-small-en-us-0.15")
    recognizer = vosk.KaldiRecognizer(model, 16000, vocabulary)

    # Take microphone input
    mic = pyaudio.PyAudio()
    stream = mic.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=8192)
    stream.start_stream()

    try_again_flag = False
    repeat_definition_flag = True
    counter = 0
    # Read and interpret words -- if successful, Cozmo repeats what you just said
    while counter < dict_length:
        attempts = 0
        correct = False
        definition = dictionary.get(dict_keys[counter])[0]
        word = dict_keys[counter]

        robot.say_text(definition).wait_for_completed()

        while not correct:

            text = get_text_from_audio(stream, recognizer)

            # This code feels like it's garbage
            # If the try_again_flag is set, make user stuck in the first part of the loop until he says yes or no
            if try_again_flag:
                if text == 'yes':
                    try_again_flag = False
                    robot.say_text("Do you want to hear the definition again?").wait_for_completed()
                    repeat_definition_flag = True
                    continue
                elif text == 'no':
                    try_again_flag = False
                    break
                else:
                    continue

            if repeat_definition_flag:
                if text == 'yes':
                    repeat_definition_flag = False
                    robot.say_text(definition).wait_for_completed()
                elif text == 'no':
                    repeat_definition_flag = False
                else:
                    continue

            # TODO: Create a function for yes / no statement detection

            # If the user answers, then check if the answer is correct
            if text:
                attempts += 1

                correct = check_answer(text, word)

                if correct:
                    robot.say_text("Correct! Good Job!").wait_for_completed()

                if not correct:
                    robot.say_text("That is not correct.").wait_for_completed()
                    try_again_flag = True
                    robot.say_text("Would you like to try again?").wait_for_completed()
                    # TODO: Check for actual answer, likely a boolean flag needed.

        counter += 1

    robot.say_text(
        "We are now done with the vocabulary training. Please say [word] to continue to the dialogue training.").wait_for_completed()

    # TODO: Alternative code structure, ask for confirmation at the name and gender section separately instead of at the end?
    correct = False

    ###################### Is this really necessary? #################################
    name = ""
    anrede = ""
    ###################### Is this really necessary? #################################
    while not correct:

        robot.say_text("Ich heiße Frau Meier in diesem Szenario, wie heißen Sie?").wait_for_completed()

        name = get_words(recognizer, stream)

        robot.say_text("Soll ich Sie mit Herr oder Frau anreden?").wait_for_completed()

        # The only possible answers here are "Herr" or "Frau", nothing else is accepted. A bit close-minded?
        while True:
            anrede = get_text_from_audio(stream, recognizer)

            herr = check_answer(anrede, "herr")
            frau = check_answer(anrede, "frau")

            if herr or frau:
                break
            else:
                robot.say_text("Entschuldigung, ich habe das nicht verstanden. Können Sie es nochmal wiederholen?")

        robot.say_text("Danke. Also Sie heißen {} {}. Ist das richtig?".format(anrede, name)).wait_for_completed()

        while True:
            text = get_text_from_audio(stream, recognizer)

            # Check if answer includes "ja" or "nein"
            ja = check_answer(text, "ja")
            nein = check_answer(text, "nein")

            if ja:
                correct = True
                break
            elif nein:
                correct = False
                break

    robot.say_text("Ok, dann fangen wir an.").wait_for_completed()

    lines = [
        "Guten Tag {} {}. Ich bin Frau Meier die Personalchefin. Ich werde heute mit Ihnen das Interview durchführen.".format(
            anrede, name),
        "Warum möchten Sie ausgerechnet bei uns arbeiten?",
        "Warum meinen Sie, dass Sie für diese Stelle geeignet sind?",
        "Welche Fremdsprachenkenntnisse haben Sie?",
        "Sie sprechen gut Deutsch. Aber können Sie auch Deutsch schreiben?",
        "Was sind Ihre persönlichen Stärken?",
        "Wie sehen Sie Ihre berufliche Zukunft?",
        "Vielen Dank {} {}, ich werde Sie in 2 Tagen anrufen. Vielen Dank. Auf Wiedersehen.".format(anrede, name)]

    for line in lines:
        print(line)
        robot.say_text(line).wait_for_completed()

        something_said = False
        stopped_talking = False

        while not something_said and not stopped_talking:

            text = get_text_from_audio(stream, recognizer)

            if text:
                something_said = True
            elif something_said:
                stopped_talking = True


cozmo.robot.Robot.drive_off_charger_on_connect = False
cozmo.run_program(cozmo_program)

# TODO: Feedback to correct/ false responses, use animations too
# TODO: Log the face & emotion detection
# TODO: Test if the code actually works
# TODO: List of words that are correct instead of a singular one? Just do it outside of check_answer
# TODO: What if some user says something like "Yes! Wait nono no nono"?
# TODO: The user should be able to give the answer while Cozmo is talking. Something with the .wait_for_completed() method.
# TODO: Potential feature: "I might not understand this word. Do you want to type it with a keyboard?"
# TODO: Maybe this whole idea could work with cubes. Press on a cube to move on, maybe to repeat the definition again (AFTER PROTOTYPE)
