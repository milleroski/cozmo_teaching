import cozmo
import vosk
import pyaudio
import json
import random
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

def check_answer(text, phrase):
    if phrase in text:
        return True

    return False


def say_text(text, robot):
    robot.say_text(text, duration_scalar=0.7).wait_for_completed()


def cozmo_program(robot: cozmo.robot.Robot):
    # Move Cozmo's head up and the lift down
    print("current battery voltage: " + str(robot.battery_voltage) + "V")

    robot.set_robot_volume(0.2)
    robot.move_lift(-3)
    robot.set_head_angle(cozmo.robot.MAX_HEAD_ANGLE).wait_for_completed()  # This doesn't work sometimes?

    # Load in a dictionary, for implementation see Dictionary.py
    dictionary = load_dictionary()
    dict_keys = list(dictionary.keys())
    dict_length = len(dictionary)

    # Lists of good, bad, and neutral animations
    bad_animations = [4, 5, 17, 21, 25, 27, 54, 63, 64, 65]
    neutral_animations = [3, 18, 22, 40, 51, 58, 61, 77, 78, 80]
    good_animations = [1, 7, 23, 26, 30, 31, 35, 50, 57, 68]

    # Vocabulary that the user is likely to use, otherwise vosk will very likely misinterpret it
    confirmation_words = ["yes", "no", "yeah", "nope", "sure", "correct"]
    vocabulary = json.dumps(dict_keys + confirmation_words)
    print(vocabulary)

    # Load in the vosk model
    model = vosk.Model(r"D:\Programming\CozmoSDK\cozmo_teaching\Model\vosk-model-small-en-us-0.15")
    recognizer = vosk.KaldiRecognizer(model, 16000, vocabulary)

    # Take microphone input
    mic = pyaudio.PyAudio()
    stream = mic.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=8192)
    stream.start_stream()

    try_again_flag = False
    repeat_definition_flag = False
    counter = 0
    # Read and interpret words -- if successful, Cozmo repeats what you just said
    while counter < dict_length:
        attempts = 0
        correct = False
        definition = dictionary.get(dict_keys[counter])[0]
        word = dict_keys[counter]

        say_text(definition, robot)

        while not correct:

            text = get_text_from_audio(stream, recognizer)

            print(text)
            # This code feels like it's garbage
            # If the try_again_flag is set, make user stuck in the first part of the loop until he says yes or no
            if try_again_flag:
                if text == 'yes':
                    try_again_flag = False
                    say_text("Do you want to hear the definition again?", robot)
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
                    say_text(definition, robot)
                    continue
                elif text == 'no':
                    say_text("Alright. You may speak now.", robot)
                    repeat_definition_flag = False
                    continue
                else:
                    continue

            # TODO: Create a function for yes / no statement detection

            # If the user answers, then check if the answer is correct
            if text:
                attempts += 1

                correct = check_answer(text, word)

                if correct:
                    say_text("Correct! Good Job!", robot)
                    robot.play_anim_trigger(
                        robot.anim_triggers[good_animations[random.randint(0, 9)]]).wait_for_completed()

                if not correct:
                    say_text("That is not correct.", robot)
                    robot.play_anim_trigger(
                        robot.anim_triggers[bad_animations[random.randint(0, 9)]]).wait_for_completed()
                    try_again_flag = True
                    say_text("Would you like to try again?", robot)

        counter += 1

    say_text(
        "We are now done with the vocabulary training. Please say [word] to continue to the dialogue training.", robot)

    # TODO: Alternative code structure, ask for confirmation at the name and gender section separately instead of at the end?

    say_text("Ok, let's get started then.", robot)

    lines = [
        "ring ring...ring ring...ring ring...",
        "Yes, this is Cozmo calling. May I speak to Mr. Franks, please?",
        "Uhm...actually, this call is rather urgent. We spoke yesterday about a delivery problem that Mr. Franks "
        "mentioned. Did he leave any information with you?",
        "Yes, the shipment was delayed from France. But it is on the way now. Could I schedule a meeting with Mr. "
        "Frank on Thursday afternoon?",
        "Unfortunately, that doesn't suit me. Is he doing anything on Friday morning?",
        "Great, should I come by at 9?",
        "Yes, 10 would be great.",
        "No, I think that's everything. Thank you for your help...Goodbye."]

    for line in lines:
        print(line)
        say_text(line, robot)

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

# Fill
# TODO: Feedback to correct/ false responses, use animations too
# TODO: Log the face & emotion detection
# TODO: Test if the code actually works
# TODO: List of words that are correct instead of a singular one? Just do it outside of check_answer
# TODO: What if some user says something like "Yes! Wait nono no nono"?
# TODO: The user should be able to give the answer while Cozmo is talking. Something with the .wait_for_completed() method.
# TODO: Potential feature: "I might not understand this word. Do you want to type it with a keyboard?"
# TODO: Maybe this whole idea could work with cubes. Press on a cube to move on, maybe to repeat the definition again (AFTER PROTOTYPE)
