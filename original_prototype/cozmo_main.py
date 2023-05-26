import cozmo
from cozmo.util import degrees
import cozmo.faces
import vosk
import pyaudio
import threading
import json
import random
import asyncio
import time
import logging
import os
from DictionaryEnglish import load_dictionary

# logging.basicConfig(filename='logging.log', level=logging.DEBUG)
logging.basicConfig(
    filename='logging.log',
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.DEBUG,
    datefmt='%Y-%m-%d %H:%M:%S')

# This condition is used to stop the thread looping follow_face
condition = threading.Event()

# This chunk of code HAS to be declared in the outer scope because of the get_text_from_audio function
# Otherwise the recognizer and stream parameters remain static, which messes the speech detection up
# Load in the vosk model
model = vosk.Model(os.path.abspath("vosk-model-small-en-us-0.15"))
recognizer = vosk.KaldiRecognizer(model, 16000)
# recognizer = vosk.KaldiRecognizer(model, 16000, vocabulary)

# Take microphone input
mic = pyaudio.PyAudio()
stream = mic.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=8192)


def sense_bump(robot: cozmo.robot.Robot, save_acc):
    sensibility = 1000
    if save_acc._x > robot.accelerometer._x + sensibility or save_acc._x < robot.accelerometer._x - sensibility:
        return True
    if save_acc._y > robot.accelerometer._y + sensibility or save_acc._y < robot.accelerometer._y - sensibility:
        return True
    if save_acc._z > robot.accelerometer._z + sensibility or save_acc._z < robot.accelerometer._z - sensibility:
        return True
    return False


# Code taken from animation.py, written by Maximilian
def fist_bump(robot: cozmo.robot.Robot):
    robot.play_anim_trigger(robot.anim_triggers[199], in_parallel=True, ignore_body_track=True).wait_for_completed()
    time.sleep(.5)
    save_acc = robot.accelerometer
    while not sense_bump(robot, save_acc):
        # If 3 seconds pass, repeat give me a fist bump
        pass
    robot.play_anim_trigger(robot.anim_triggers[201], in_parallel=True, ignore_body_track=True).wait_for_completed()
    robot.set_head_angle(cozmo.robot.MAX_HEAD_ANGLE, in_parallel=True).wait_for_completed()
    robot.set_lift_height(0, in_parallel=True)


def get_text_from_audio():
    data = stream.read(4096, exception_on_overflow=False)

    if recognizer.AcceptWaveform(data):
        return recognizer.Result()[14:-3]


def get_words():
    name = ""
    while not name:
        name = get_text_from_audio()
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


def handle_face_observed(evt, face: cozmo.faces.Face, **kwargs):
    logging.info(face.expression + "-" + str(face.expression_score))


def follow_face(robot: cozmo.robot.Robot):
    # TODO: Shut down thread if the user is done with the entire program
    robot.enable_facial_expression_estimation()
    logging.info("Following face...")
    face_to_follow = None
    while not condition.is_set():
        time.sleep(1)
        turn_action = None
        if face_to_follow:
            # start turning towards the face
            robot.add_event_handler(cozmo.faces.EvtFaceObserved, handle_face_observed)
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
    robot.set_robot_volume(0.7)
    logging.info("Preparation started...")
    logging.info("current battery voltage: " + str(robot.battery_voltage) + "V")

    robot.set_head_angle(cozmo.robot.MAX_HEAD_ANGLE, in_parallel=True).wait_for_completed()
    robot.set_lift_height(0, in_parallel=True)
    # Load in a dictionary, for implementation see DictionaryGerman.py
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
    logging.info(vocabulary)

    logging.info("Preparation ended...")
    # -------------Initiation and name-----------------------
    logging.info("Initiation started...")
    say_text("Hi there! I'm Cozmo! Your language learning companion!", robot)
    say_text("You can interact with me through the microphone when I ask questions!", robot)
    say_text("Please try to give short answers if possible, as I'm still learning how to interact with humans!", robot)
    say_text("What is your name? Please answer with ONLY, your name, not with a sentence", robot)

    something_said = False
    stopped_talking = False
    name = ""

    stream.start_stream()

    while not (something_said and stopped_talking):

        text = get_text_from_audio()

        if text:
            logging.info(text)
            name += text
            something_said = True

        elif something_said:
            stopped_talking = True

            say_text("So your name is {}, correct?".format(name), robot)
            question_answered = False
            while not question_answered:

                text = get_text_from_audio()

                if text:
                    if check_answer(text, "yes"):
                        question_answered = True
                    elif check_answer(text, "no"):
                        question_answered = True
                        something_said = False
                        stopped_talking = False
                        name = ""
                        say_text("Ok, what is your name?", robot)

    stream.stop_stream()
    logging.info("Exiting name loop...")
    say_text("Ok, {}, Give me a fist bump!".format(name), robot)

    logging.info("Starting fist bump...")
    fist_bump(robot)
    logging.info("Ending fist bump...")

    say_text("Today, we will do a vocabulary quiz. I will give you {} vocabulary questions that you need to answer".format(str(dict_length)),
             robot)
    say_text("These words should be familiar to you from your class with Ms. Ellen Donder.", robot)
    say_text("Ok, let's get started!", robot)
    logging.info("End of introduction...")
    # -------------Start of definition quiz------------------
    logging.info("Start of vocabulary exercise...")
    try_again_flag = False
    counter = 0
    first_try_counter = 0

    stream.start_stream()
    while counter < dict_length:
        logging.info("In main loop, question {} of {}".format(counter, dict_length))
        attempts = 0
        correct = False
        first_try = True
        definition = dictionary.get(dict_keys[counter])[0]
        word = dict_keys[counter]

        say_text("Question {}, {}".format(str(counter + 1), definition), robot)

        while not correct:
            text = get_text_from_audio()

            # If the try_again_flag is set, make user stuck in the first part of the loop until he says yes or no
            if try_again_flag:

                logging.info("User answering try_again...")

                # Add long string of confirmation and denial words
                if text == 'yes':
                    try_again_flag = False
                    say_text("Question {}, {}".format(str(counter + 1), definition), robot)

                elif text == 'no':
                    try_again_flag = False
                    say_text("The word is {}.".format(word), robot)
                    say_text("It means {}".format(definition), robot)
                    break

                continue

            # If the user answers, then check if the answer is correct
            if text:

                logging.info(text)

                correct = check_answer(text, word)

                if correct:
                    logging.info("Correct answer...")
                    say_text("Correct! Good Job!", robot)
                    number = random.randint(0, 9)
                    logging.info("Animation number " + str(number))
                    robot.play_anim_trigger(
                        robot.anim_triggers[good_animations[number]],
                        in_parallel=True, ignore_body_track=True).wait_for_completed()
                    robot.set_head_angle(cozmo.robot.MAX_HEAD_ANGLE, in_parallel=True).wait_for_completed()
                else:
                    logging.info("Incorrect answer...")
                    first_try = False
                    attempts += 1
                    say_text("That is not correct.", robot)
                    number = random.randint(0, 9)
                    logging.info("Animation number " + str(number))
                    robot.play_anim_trigger(
                        robot.anim_triggers[bad_animations[random.randint(0, 9)]],
                        in_parallel=True, ignore_body_track=True).wait_for_completed()
                    robot.set_head_angle(cozmo.robot.MAX_HEAD_ANGLE, in_parallel=True).wait_for_completed()
                    try_again_flag = True
                    say_text("Would you like to try again?", robot)
                    # Something after this flag broke

        if first_try:
            first_try_counter += 1

        counter += 1

    stream.stop_stream()
    logging.info("End of main vocabulary part...")
    logging.info("Start of vocabulary exercise summary...")
    score = first_try_counter / dict_length
    percentage = score * 100

    logging.info("{} = {}/{}".format(float(percentage), int(dict_length), int(first_try_counter)))

    say_text("First of all, good job buddy!, give me a fist bump!", robot)
    fist_bump(robot)
    say_text("You got {} correct answers out of {} questions. That is a {} percentage.".format(first_try_counter,
                                                                                               dict_length, percentage),
             robot)

    if percentage >= 90:
        say_text("Fantastic job! I'm impressed!", robot)
    elif percentage >= 70:
        say_text("Good job! That was good!", robot)
    elif percentage >= 50:
        say_text("You are getting there. Don't give up and let's keep practicing!", robot)
    else:
        say_text("It's not that easy, but I'm glad that you are trying, don't give up and let's practice again next "
                 "time!", robot)

    robot.play_anim_trigger(
        robot.anim_triggers[good_animations[random.randint(0, 9)]],
        in_parallel=True, ignore_body_track=True).wait_for_completed()

    logging.info("End of vocabulary exercise...")
    # -------------End of definition quiz------------------
    say_text(
        "We are now done with the vocabulary training. Please say okay to continue to the dialogue training.", robot)

    stream.start_stream()
    while True:
        text = get_text_from_audio()

        if text:
            logging.info(text)
            word_said = check_answer(text, "okay")

            if word_said:
                break

    stream.stop_stream()
    # ------------Beginning of dialogue training--------------

    logging.info("Starting dialogue exercise...")

    say_text(
        "We will now practice dialogue. You should have a sheet of paper in front of you. You can speak in full sentences!",
        robot)
    say_text("Ok, here we go!", robot)

    lines = [
        "ring ring, ring ring, ring ring",
        "Yes, this is Cozmo calling. May I speak to Mr. Franks, please?",
        "Uhm...actually, this call is rather urgent. We spoke yesterday about a delivery problem that Mr. Franks "
        "mentioned. Did he leave any information with you?",
        "Yes, the shipment was delayed from France. But it is on the way now. Could I schedule a meeting with Mr. "
        "Frank on Thursday afternoon?",
        "Unfortunately, that doesn't suit me. Is he doing anything on Friday morning?",
        "Great, should I come by at 9?",
        "Yes, 10 would be great.",
        "No, I think that's everything. Thank you for your help...Goodbye."]

    stream.start_stream()
    for line in lines:
        logging.info(line)
        say_text(line, robot)

        timeout = 10  # [seconds]
        timeout_start = time.time()  # [seconds]

        while time.time() < timeout_start + timeout:
            data = stream.read(4096, exception_on_overflow=False)

            text = recognizer.PartialResult()[17:-3]

            if text:
                logging.info(text)
                timeout_start = time.time()
                timeout = 3

            if recognizer.AcceptWaveform(data):
                sentence = recognizer.Result()[14:-3]

    stream.stop_stream()

    say_text("This is the end of the dialogue training.", robot)

    logging.info("End of study dialogue")

    say_text("Thank you for participating in the study, you helped me learn more about humans, and I hope you had "
             "fun. Give me one last fist bump!", robot)
    fist_bump(robot)
    say_text("Thank youuuu, goodbye!", robot)
    robot.play_anim_trigger(
        robot.anim_triggers[213],
        in_parallel=True, ignore_body_track=True).wait_for_completed()


def main(robot: cozmo.robot.Robot):
    cozmo.robot.Robot.drive_off_charger_on_connect = False
    t1 = threading.Thread(target=cozmo_program, args=(robot,))
    t2 = threading.Thread(target=follow_face, args=(robot,))
    logging.info("Thread 1 started...")
    logging.info("Thread 2 started...")
    t1.start()
    t2.start()
    t1.join()
    logging.info("Thread 1 finished...")
    condition.set()
    t2.join()
    logging.info("Thread 2 finished...")
    logging.info("Shutting down...")


if __name__ == "__main__":
    cozmo.run_program(main)

# Fill
# TODO: Log the face & emotion detection (ALMOST DONE)
# TODO: Potential feature: "I might not understand this word. Do you want to type it with a keyboard?"
# TODO: Maybe this whole idea could work with cubes. Press on a cube to move on, maybe to repeat the definition again (AFTER PROTOTYPE)
