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

def check_answer(text, title, robot):
    word_list = text.split()
    correct_answer = False
    print(title)

    for word in word_list:
        if word == title.casefold():
            correct_answer = True
            robot.say_text("Richtig! Gut gemacht!").wait_for_completed()
            break

    if not correct_answer:
        robot.say_text("Das ist nicht korrekt.").wait_for_completed()

    return correct_answer


def cozmo_program(robot: cozmo.robot.Robot):
    # Move Cozmos head up and the lift down
    robot.move_lift(-3)
    robot.set_head_angle(cozmo.robot.MAX_HEAD_ANGLE).wait_for_completed()   # This doesn't work sometimes?

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
        current_definition = dictionary.get(dict_keys[counter])[0]
        current_word = dict_keys[counter]
        robot.say_text(current_definition).wait_for_completed()

        # TODO: Make this a function for readability maybe get rid of second while loop completely if possible?
        while not correct:

            text = get_text_from_audio(stream, recognizer)

            if text:

                # This is a manual override function, there's a better, but much more involved solution for this
                if text == 'weiter':
                    break

                correct = check_answer(text, current_word, robot)

                if not correct:
                    # TODO: Maybe this whole idea could work with cubes. Press on a cube to move on, maybe to repeat the definition again (AFTER PROTOTYPE)
                    # robot.say_text("Do you want to try again?")
                    robot.say_text("Willst du es nochmal versuchen?").wait_for_completed()
        counter += 1

    robot.say_text(
        "Wir sind jetzt mit den Vokabulartraining fertig. Jetzt machen wir eine Dialogübung.").wait_for_completed()

    correct = False
    while not correct:

        robot.say_text("Ich heiße Frau Meier in diesem Szenario, wie heißen Sie?").wait_for_completed()

        name = ""
        while not name:

            name = get_text_from_audio(stream, recognizer)

        robot.say_text("Soll ich Sie mit Herr oder Frau anreden?")

        anrede = ""
        while not anrede:

            anrede = get_text_from_audio(stream, recognizer)

        # Format this better, use actual formatting instead
        robot.say_text("Danke. Also Sie heißen " + anrede + " " + name + ". Ist das richtig?").wait_for_completed()

        text = ""
        while not text:
            text = get_text_from_audio(stream, recognizer)

            if text == "ja":
                correct = True
                break
            elif text == "nein":
                break


    # Ja / Nein option

    robot.say_text("Ok, dann fangen wir an.").wait_for_completed()

    # Reusing dictionary code
    lines = [
        "Guten Tag " + anrede + " " + name + ". Ich bin Frau Meier die Personalchefin. Ich werde heute mit Ihnen das Interview durchführen.",
        "Warum möchten Sie ausgerechnet bei uns arbeiten?",
        "Warum meinen Sie, dass Sie für diese Stelle geeignet sind?",
        "Welche Fremdsprachenkenntnisse haben Sie?",
        "Sie sprechen gut Deutsch. Aber können Sie auch Deutsch schreiben?",
        "Was sind Ihre persönlichen Stärken?",
        "Wie sehen Sie Ihre berufliche Zukunft?",
        "Vielen Dank " + anrede + " " + name + ", ich werde Sie in 2 Tagen anrufen. Vielen Dank. Auf Wiedersehen."]

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

# TODO: German dialogue practice
# TODO: The user should be able to give the answer while Cozmo is talking. Something with the .wait_for_completed() method.
# TODO: Potential feature: "I might not understand this word. Do you want to type it with a keyboard?"

# TODO: Integrate Dictionary with Cozmo
# TODO: Add translation vocabulary training
# TODO: Face & Emotion detection
# TODO: Feedback to correct/ false responses, use animations too
