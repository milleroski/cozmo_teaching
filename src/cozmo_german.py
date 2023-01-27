import cozmo
import vosk
import pyaudio
from Dictionary import load_dictionary


# Check if the user has mentioned the correct word
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

    # Load in the vosk model
    model = vosk.Model(r"D:\Programming\VOSK\Model\vosk-model-small-de-0.15")
    recognizer = vosk.KaldiRecognizer(model, 16000)

    # Take microphone input
    mic = pyaudio.PyAudio()
    stream = mic.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=8192)
    stream.start_stream()

    counter = 0
    # Read and interpret words -- if successful, Cozmo repeats what you just said
    while counter < dict_length:
        correct = False
        definition = dictionary.get(dict_keys[counter])[0]
        word = dict_keys[counter]

        robot.say_text(definition).wait_for_completed()

        while not correct:

            text = get_text_from_audio(stream, recognizer)

            # If the user answers, then check if the answer is correct
            if text:

                # This is a manual override function, there's a better, but much more involved solution for this
                if text == 'weiter':
                    break

                correct = check_answer(text, word)

                if correct:
                    robot.say_text("Richtig! Gut gemacht!").wait_for_completed()

                if not correct:
                    robot.say_text("Das ist nicht korrekt.").wait_for_completed()
                    robot.say_text("Willst du es nochmal versuchen?").wait_for_completed()
                    # TODO: Check for actual answer, likely a boolean flag needed.

        counter += 1

    robot.say_text(
        "Wir sind jetzt mit den Vokabulartraining fertig. Jetzt machen wir eine Dialogübung.").wait_for_completed()

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

# TODO: Log the face & emotion detection
# TODO: Test if the code actually works
# TODO: List of words that are correct instead of a singular one? Just do it outside of check_answer
# TODO: What if some user says something like "Yes! Wait nono no nono"?
# TODO: German dialogue practice
# TODO: The user should be able to give the answer while Cozmo is talking. Something with the .wait_for_completed() method.
# TODO: Potential feature: "I might not understand this word. Do you want to type it with a keyboard?"
# TODO: Maybe this whole idea could work with cubes. Press on a cube to move on, maybe to repeat the definition again (AFTER PROTOTYPE)
# TODO: Integrate Dictionary with Cozmo
# TODO: Add translation vocabulary training
# TODO: Feedback to correct/ false responses, use animations too
