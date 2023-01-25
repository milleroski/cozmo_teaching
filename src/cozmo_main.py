import cozmo
from cozmo.util import degrees
import vosk
import pyaudio
import threading
import json
import random
import asyncio
import time
from Dictionary import load_dictionary

# TODO: Make robot global variable?
robot = cozmo.robot.Robot
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


def say_text(text, robot: cozmo.robot.Robot):
    robot.say_text(text, duration_scalar=0.7, in_parallel=True).wait_for_completed()


def follow_face(robot: cozmo.robot.Robot):
    robot.enable_facial_expression_estimation()
    print("Following face...")
    face_to_follow = None
    while True:
        time.sleep(1)
        turn_action = None
        if face_to_follow:
            # start turning towards the face
            # print(cozmo.faces.Face.expression)
            turn_action = robot.turn_towards_face(face_to_follow, in_parallel=True)
        if not (face_to_follow and face_to_follow.is_visible):
            # find a visible face, timeout if nothing found after a short while
            try:
                face_to_follow = robot.world.wait_for_observed_face(timeout=1)
            except asyncio.TimeoutError:
                turn_action = robot.turn_in_place(degrees(45), in_parallel=True)
                face_to_follow = None

        if turn_action:
            # Complete the turn action if one was in progress
            turn_action.wait_for_completed()


def cozmo_program(robot: cozmo.robot.Robot):
    # Move Cozmo's head up and the lift down
    print("current battery voltage: " + str(robot.battery_voltage) + "V")

    robot.set_robot_volume(0.2)
    robot.set_head_angle(cozmo.robot.MAX_HEAD_ANGLE, in_parallel=True).wait_for_completed()
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
    # TODO: Create a custom model with INCREASED weights for correct words, but not ONLY those words
    # TODO: If not enough time, throw in a json with like 10000 most commonly used english words that don't confilict with the definitions
    model = vosk.Model(r"D:\Programming\CozmoSDK\cozmo_teaching\Model\vosk-model-small-en-us-0.15")
    recognizer = vosk.KaldiRecognizer(model, 16000, vocabulary)

    # Take microphone input
    mic = pyaudio.PyAudio()
    stream = mic.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=8192)
    stream.start_stream()

    # -------------Initiation and name-----------------------
    say_text("Hi there! I'm Cozmo! What is your name?", robot)

    something_said = False
    stopped_talking = False
    name = ""
    while not something_said and not stopped_talking:

        text = get_text_from_audio(stream, recognizer)

        if text:
            name += text
            something_said = True

        elif something_said:
            stopped_talking = True

            say_text("So your name is {}, correct?".format(name), robot)
            question_answered = False
            while not question_answered:

                text = get_text_from_audio(stream, recognizer)

                if check_answer(text, "yes"):
                    question_answered = True
                elif check_answer(text, "no"):
                    question_answered = True
                    something_said = False
                    stopped_talking = False
                    say_text("Ok, what is your name?", robot)

    say_text("Ok, {}, Give me a fist bump!".format(name), robot)

    #TODO: Insert fist bump code here

    say_text("Today, we will do a vocabulary quiz. I will give you 10 vocabulary questions that you need to answer", robot)
    say_text("These words should be familiar to you from your class with Ms. Ellen Donder.", robot)
    say_text("Ok, let's get started!", robot)
    # -------------Start of definition quiz------------------
    try_again_flag = False
    repeat_definition_flag = False
    counter = 0

    while counter < dict_length:
        attempts = 0
        correct = False
        definition = dictionary.get(dict_keys[counter])[0]
        word = dict_keys[counter]

        say_text(definition, robot)
        while not correct:
            text = get_text_from_audio(stream, recognizer)

            # This code feels like it is garbage
            # If the try_again_flag is set, make user stuck in the first part of the loop until he says yes or no
            if try_again_flag:
                if text == 'yes':
                    try_again_flag = False
                    say_text("Do you want to hear the definition again?", robot)
                    repeat_definition_flag = True

                elif text == 'no':
                    try_again_flag = False
                    break

                continue

            if repeat_definition_flag:
                if text == 'yes':
                    repeat_definition_flag = False
                    say_text(definition, robot)

                elif text == 'no':
                    say_text("Alright. You may speak now.", robot)
                    repeat_definition_flag = False

                continue

            # If the user answers, then check if the answer is correct
            if text:

                correct = check_answer(text, word)

                if correct:
                    say_text("Correct! Good Job!", robot)
                    number = random.randint(0, 9)
                    print("Animation number " + str(number))
                    robot.play_anim_trigger(
                        robot.anim_triggers[good_animations[number]],
                        in_parallel=True, ignore_head_track=True).wait_for_completed()
                    robot.set_head_angle(cozmo.robot.MAX_HEAD_ANGLE, in_parallel=True).wait_for_completed()

                if not correct:
                    attempts += 1
                    say_text("That is not correct.", robot)
                    robot.play_anim_trigger(
                        robot.anim_triggers[bad_animations[random.randint(0, 9)]],
                        in_parallel=True, ignore_head_track=True).wait_for_completed()
                    robot.set_head_angle(cozmo.robot.MAX_HEAD_ANGLE, in_parallel=True).wait_for_completed()
                    try_again_flag = True
                    say_text("Would you like to try again?", robot)

                time.sleep(1)

        counter += 1

    # -------------End of definition quiz------------------
    say_text(
        "We are now done with the vocabulary training. Please say [word] to continue to the dialogue training.", robot)

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


def main(robot: cozmo.robot.Robot):
    cozmo.robot.Robot.drive_off_charger_on_connect = False
    t1 = threading.Thread(target=cozmo_program, args=(robot,))
    t2 = threading.Thread(target=follow_face, args=(robot,))
    t2.start()
    t1.start()
    t1.join()
    t2.join()


if __name__ == "__main__":
    cozmo.run_program(main, use_viewer=True, force_viewer_on_top=True)

# Fill
# TODO: Log the face & emotion detection
# TODO: Test if the code actually works
# TODO: Potential feature: "I might not understand this word. Do you want to type it with a keyboard?"
# TODO: Maybe this whole idea could work with cubes. Press on a cube to move on, maybe to repeat the definition again (AFTER PROTOTYPE)
