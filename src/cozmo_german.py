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
import datetime
from DictionaryGerman import load_dictionary

currentDT = datetime.datetime.now()
FileName = currentDT.strftime("%Y_%m_%d_%H_%M_%S") + "_cozmo_english.log"

# logging.basicConfig(filename='logging.log', level=logging.DEBUG)
logging.basicConfig(
    filename=FileName,
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.DEBUG,
    datefmt='%Y-%m-%d %H:%M:%S')

# This condition is used to stop the thread looping follow_face
condition = threading.Event()

# This chunk of code HAS to be declared in the outer scope because of the get_text_from_audio function
# Otherwise the recognizer and stream parameters remain static, which messes the speech detection up
# Load in the vosk model
model = vosk.Model(os.path.abspath("vosk-model-small-de-0.15"))
recognizer = vosk.KaldiRecognizer(model, 16000)

# Take microphone input
mic = pyaudio.PyAudio()
stream = mic.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=8192)


def sense_bump(robot: cozmo.robot.Robot, save_acc):
    sensibility = 3500
    if save_acc._x > robot.accelerometer._x + sensibility or save_acc._x < robot.accelerometer._x - sensibility:
        return True
    if save_acc._y > robot.accelerometer._y + sensibility or save_acc._y < robot.accelerometer._y - sensibility:
        return True
    if save_acc._z > robot.accelerometer._z + sensibility or save_acc._z < robot.accelerometer._z - sensibility:
        return True
    return False


# Code taken from animation.py, written by Maximilian
def fist_bump(robot: cozmo.robot.Robot):
    logging.info("In fist bump")
    robot.play_anim_trigger(robot.anim_triggers[199], in_parallel=True, ignore_body_track=True,
                            ignore_head_track=True).wait_for_completed()
    save_acc = robot.accelerometer
    logging.info("Entering first bump loop...")
    while not sense_bump(robot, save_acc):
        print("In fist_bump loop")
        # If 3 seconds pass, repeat give me a fist bump
    logging.info("Exiting first bump loop...")
    robot.play_anim_trigger(robot.anim_triggers[201], in_parallel=True, ignore_body_track=True,
                            ignore_head_track=True).wait_for_completed()
    robot.set_head_angle(cozmo.robot.MAX_HEAD_ANGLE, in_parallel=True).wait_for_completed()
    robot.set_lift_height(0, in_parallel=True)


def get_text_from_audio():
    data = stream.read(4096, exception_on_overflow=False)

    if recognizer.AcceptWaveform(data):
        return recognizer.Result()[14:-3]


def check_answer_list(text, phrase):
    for word in phrase:
        correct = check_answer(text, word)

        if correct:
            return True

    return False


def check_answer(text, phrase):
    if phrase in text:
        return True

    return False


def say_text(text, robot: cozmo.robot.Robot):
    robot.say_text(text, use_cozmo_voice=False, duration_scalar=0.7, voice_pitch=1.0,
                   in_parallel=True).wait_for_completed()


def handle_face_observed(evt, face: cozmo.faces.Face, **kwargs):
    logging.info(face.expression + "-" + str(face.expression_score))


def follow_face(robot: cozmo.robot.Robot):
    robot.enable_facial_expression_estimation()
    logging.info("Following face...")
    face_to_follow = None
    while not condition.is_set():
        time.sleep(0.5)
        turn_action = None
        if face_to_follow:
            # Log the facial recognition...start turning towards the face
            robot.add_event_handler(cozmo.faces.EvtFaceObserved, handle_face_observed)
            # ... but only once per loop (without the oneshot it prints the result every FRAME
            cozmo.event.oneshot(handle_face_observed)

            # turn towards the face
            turn_action = robot.turn_towards_face(face_to_follow, in_parallel=True)

        if not (face_to_follow and face_to_follow.is_visible):
            logging.info("Lost face, searching...")

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
    logging.info("Preparation started...")
    logging.info("current battery voltage: " + str(robot.battery_voltage) + "V")

    robot.set_robot_volume(0.7)
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
    confirmation_words = ["ja", "richtig", "ist korrekt", "ist wahr", "jawohl", "klar"]
    denial_words = ["nein", "ne", "nicht korrekt", "falsch", "ist nicht wahr"]
    vocabulary = json.dumps(dict_keys + confirmation_words)
    logging.info(vocabulary)

    logging.info("Preparation ended...")
    # -------------Initiation and name-----------------------
    logging.info("Start of introduction...")
    say_text("Hallo! Ich bin Cozmo!", robot)
    say_text("Wenn ich dir fragen stelle kannst du mir durch das Mikrofon antworten!", robot)
    say_text("Bitte versuche deine Antworten so kurz wie möglich zu halten, ich lerne immer noch wie Menschen "
             "funktionieren!", robot)
    say_text("Wie heißen Sie? Bitte antworten Sie NUR mit ihren Namen, nicht mit einem Satz", robot)

    something_said = False
    stopped_talking = False
    name = ""

    stream.start_stream()
    logging.info("Entering name loop...")
    while not (something_said and stopped_talking):

        text = get_text_from_audio()

        if text:
            logging.info("Name: " + text)
            name += text
            something_said = True

        elif something_said:
            stopped_talking = True

            say_text("Also heißen Sie {}, richtig?".format(name), robot)
            question_answered = False
            while not question_answered:

                text = get_text_from_audio()

                if text:
                    logging.info("Confirmation: " + text)
                    if check_answer_list(text, confirmation_words):
                        question_answered = True
                    elif check_answer_list(text, denial_words):
                        question_answered = True
                        something_said = False
                        stopped_talking = False
                        name = ""
                        say_text("Ok, wie heißen Sie", robot)

    stream.stop_stream()
    logging.info("Exiting name loop...")
    say_text("Ok, {} gib mir einen Fauststoß!".format(name), robot)

    logging.info("Starting fist bump...")
    fist_bump(robot)
    logging.info("Ending fist bump...")

    say_text("Heute werden wir ein Vokabulartest durchführen. Ich werde dir {} Fragen stellen, und du musst die "
             "beantworten!".format(str(dict_length)),
             robot)
    say_text("Diese Begriffe solltest du schon von dem Unterricht mit Frau Ellen Donder kennen.", robot)
    say_text("Ok, los geht's!", robot)
    logging.info("End of introduction...")
    # -------------Start of definition quiz------------------
    logging.info("Start of vocabulary exercise...")
    try_again_flag = False
    counter = 0
    first_try_counter = 0

    stream.start_stream()
    while counter < dict_length:
        logging.info("In main loop, question {} of {}".format(counter, dict_length))
        correct = False
        first_try = True
        definition = dictionary.get(dict_keys[counter])[0]
        word = dict_keys[counter]

        say_text("Frage {}, {}".format(str(counter + 1), definition), robot)

        while not correct:
            text = get_text_from_audio()

            # If the user answers, then check if the answer is correct
            if text:

                logging.info(text)

                # If the try_again_flag is set, make user stuck in the first part of the loop until he says yes or no
                if try_again_flag:

                    logging.info("User answering try_again...")

                    # Add long string of confirmation and denial words
                    if check_answer_list(text, confirmation_words):
                        try_again_flag = False
                        say_text("Frage {}, {}".format(str(counter + 1), definition), robot)

                    elif check_answer_list(text, denial_words):
                        try_again_flag = False
                        say_text("Das Wort ist {}.".format(word), robot)
                        say_text("Die Definition lautet {}".format(definition), robot)
                        break

                    continue

                correct = check_answer(text, word)

                print(text)
                print(word)

                if correct:
                    logging.info("Correct answer: {} {}".format(text, word))
                    say_text("Richtig! Gut gemacht!", robot)
                    number = random.randint(0, 9)
                    logging.info("Good animation number " + str(number))
                    robot.play_anim_trigger(
                        robot.anim_triggers[good_animations[number]],
                        in_parallel=True, ignore_body_track=True).wait_for_completed()
                    robot.set_head_angle(cozmo.robot.MAX_HEAD_ANGLE, in_parallel=True).wait_for_completed()
                else:
                    logging.info("Incorrect answer: {} {}".format(text, word))
                    first_try = False
                    say_text("Das ist leider falsch.", robot)
                    number = random.randint(0, 9)
                    logging.info("Bad animation number " + str(number))
                    robot.play_anim_trigger(
                        robot.anim_triggers[bad_animations[random.randint(0, 9)]],
                        in_parallel=True, ignore_body_track=True).wait_for_completed()
                    robot.set_head_angle(cozmo.robot.MAX_HEAD_ANGLE, in_parallel=True).wait_for_completed()
                    try_again_flag = True
                    say_text("Willst du es nochmal versuchen?", robot)
                    # Something after this flag broke

        if first_try:
            first_try_counter += 1

        counter += 1

    stream.stop_stream()
    logging.info("End of vocabulary exercise...")
    logging.info("Start of vocabulary exercise summary...")
    score = first_try_counter / dict_length
    percentage = score * 100

    logging.info("{} = {}/{}".format(float(percentage), int(dict_length), int(first_try_counter)))

    say_text("Das hast du gut gemacht!, Fauststoß!", robot)
    fist_bump(robot)
    say_text("Du hast {} korrekte Antworten von {} Fragen. Das ist eine {} Prozentzahl.".format(first_try_counter,
                                                                                                dict_length,
                                                                                                percentage), robot)

    if percentage >= 90:
        say_text("Das hast du Super gemacht! Ich bin wirklich beeindruckt!", robot)
    elif percentage >= 70:
        say_text("Gut gemacht! Das war richtig gut!", robot)
    elif percentage >= 50:
        say_text("Du kommst gut voran, gib nicht auf und lass uns weiterüben!", robot)
    else:
        say_text("Es ist nicht so einfach, aber es erfreut mich das du hart arbeitest. Gib nicht auf und lass uns "
                 "nächstes mal weiterüben!", robot)

    robot.play_anim_trigger(
        robot.anim_triggers[good_animations[random.randint(0, 9)]],
        in_parallel=True, ignore_body_track=True).wait_for_completed()

    logging.info("End of vocabulary exercise summary...")
    # -------------End of definition quiz------------------
    say_text(
        "Wir sind jetzt mit der Vokabularübung fertig. Bitte sag \"Apfel\", um weiterzumachen.", robot)

    logging.info("Waiting for user confirmation word...")

    stream.start_stream()
    while True:
        text = get_text_from_audio()

        if text:
            logging.info("Confirmation word: " + text)
            word_said = check_answer(text, "apfel")

            if word_said:
                break

    stream.stop_stream()
    logging.info("Confirmation word accepted...")
    # ------------Beginning of dialogue training--------------

    logging.info("Starting dialogue exercise...")

    say_text(
        "Wir werden jetzt eine Dialogübung durchführen. Bitte lese deine Zeilen vor, und ich werde dir antworten!",
        robot)
    say_text("Bevor wie loslegen brauche ich deine Anrede, soll ich dich als Herr oder Frau anreden?", robot)

    logging.info("UNIQUE TO GERMAN VERSION: Anrede loop started...")

    anrede = ""

    stream.start_stream()

    question_answered = False
    have_anrede = False

    while not question_answered and not have_anrede:

        text = get_text_from_audio()

        if text:

            if not have_anrede:
                logging.info("Anrede: " + text)
                question_answered = False
                logging.info(text)
                herr = check_answer(text, "herr")
                frau = check_answer(text, "frau")

                if herr:
                    anrede = "herr"
                    have_anrede = True

                elif frau:
                    have_anrede = True
                    anrede = "frau"

                else:
                    continue

                say_text("Also soll ich dich {} {} nennen. Ja?".format(anrede, name), robot)

            if not question_answered:
                logging.info("User answering: " + text)

                if check_answer_list(text, confirmation_words):
                    question_answered = True
                    have_anrede = True

                elif check_answer_list(text, denial_words):
                    question_answered = True
                    have_anrede = False

                else:
                    continue

    stream.stop_stream()
    logging.info("UNIQUE TO GERMAN VERSION: Anrede loop stopped...")

    say_text("Ok {} {}, los geht's!".format(anrede, name), robot)

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

    logging.info("Entering talking loop...")
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
    logging.info("Exiting talking loop...")
    logging.info("Ending dialogue exercise...")
    say_text("Das ist das Ende vom Dialogtraining, gut gemacht!.", robot)

    logging.info("End of study dialogue...")

    say_text("Danke für deine Teilnahme in der Studie {}, ich habe viel von dir heute gelernt, und ich hoffe du "
             "hattest Spaß dabei, gib mir noch einen Fauststoß!".format(name), robot)
    fist_bump(robot)
    say_text("Tschüss!", robot)
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

# TODO: Potential feature: "I might not understand this word. Do you want to type it with a keyboard?"
# TODO: Maybe this whole idea could work with cubes. Press on a cube to move on, maybe to repeat the definition again (AFTER PROTOTYPE)
