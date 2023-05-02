import cozmo
import cozmo.faces
import threading
import json
import random
import time
from DictionaryEnglish import load_dictionary
from base_logger import logger
from face_detection import follow_face
from speech_detection import get_text_from_audio, stream, recognizer

# This condition is used to stop the thread looping in follow_face
condition = threading.Event()

#------------------------------FIST BUMP BLOCK------------------------------

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
    logger.info("In fist bump")
    robot.play_anim_trigger(robot.anim_triggers[199], in_parallel=True, ignore_body_track=True,
                            ignore_head_track=True).wait_for_completed()
    save_acc = robot.accelerometer
    logger.info("Entering first bump loop...")

    while not sense_bump(robot, save_acc):
        print("In fist_bump loop")
        # If 3 seconds pass, repeat give me a fist bump
    logger.info("Exiting first bump loop...")
    robot.play_anim_trigger(robot.anim_triggers[201], in_parallel=True, ignore_body_track=True,
                            ignore_head_track=True).wait_for_completed()
    robot.set_head_angle(cozmo.robot.MAX_HEAD_ANGLE, in_parallel=True).wait_for_completed()
    robot.set_lift_height(0, in_parallel=True)
#------------------------------FIST BUMP BLOCK------------------------------


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
    robot.say_text(text, duration_scalar=0.7, in_parallel=True).wait_for_completed()


def cozmo_program(robot: cozmo.robot.Robot):
    # Move Cozmo's head up and the lift down
    try:
        robot.set_robot_volume(0.7)
        logger.info("Preparation started...")
        logger.info("current battery voltage: " + str(robot.battery_voltage) + "V")

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

        # Vocabulary that the user is likely to use to answer
        confirmation_words = ["yes", "yet", "es", "ya", "ok", "okay", "okey", "yeah", "sure", "correct", "is true",
                              "indeed", "positive"]
        denial_words = ["no", "nope", "know", "nah", "incorrect", "is not true", "negative"]
        vocabulary = json.dumps(dict_keys + confirmation_words)
        logger.info(vocabulary)

        logger.info("Preparation ended...")
        # -------------Initiation and name-----------------------
        logger.info("Start of introduction...")
        say_text("Hi there! I'm Cozmo! Your language learning companion!", robot)
        say_text("You can interact with me through the microphone when I ask questions!", robot)
        say_text(
            "Please try to give me clear answers if possible, and repeat your answer if I do not respond to you, as I'm still learning how to interact with humans!",
            robot)
        say_text("What is your name? Please answer with ONLY, your name, not with a sentence", robot)

        something_said = False
        stopped_talking = False
        name = ""

        stream.start_stream()
        logger.info("Entering name loop...")
        while not (something_said and stopped_talking):

            text = get_text_from_audio()

            if text:
                logger.info("Name: " + text)
                name += text
                something_said = True

            elif something_said:
                stopped_talking = True

                say_text("So your name is {}, correct?".format(name), robot)
                question_answered = False
                while not question_answered:

                    text = get_text_from_audio()

                    if text:
                        logger.info("Confirmation: " + text)
                        if check_answer_list(text, confirmation_words):
                            question_answered = True
                        elif check_answer_list(text, denial_words):
                            question_answered = True
                            something_said = False
                            stopped_talking = False
                            name = ""
                            say_text("Ok, what is your name?", robot)

        stream.stop_stream()
        logger.info("Exiting name loop...")
        say_text("Ok, {}, Give me a nice fist bump!".format(name), robot)

        logger.info("Starting fist bump...")
        fist_bump(robot)
        logger.info("Ending fist bump...")

        # -------------Start of definition quiz------------------
        logger.info("End of introduction...")
        logger.info("Start of vocabulary exercise...")
        say_text(
            "Today, we will do a vocabulary quiz. I will give you {} vocabulary questions that you need to answer".format(
                str(dict_length)),
            robot)
        say_text("These words should be familiar to you from your class with Mr. Tommy Janota.", robot)
        say_text("Ok, let's get started!", robot)
        try_again_flag = False
        counter = 0
        first_try_counter = 0

        stream.start_stream()
        while counter < dict_length:
            logger.info("In main loop, question {} of {}".format(counter, dict_length))
            correct = False
            first_try = True
            definition = dictionary.get(dict_keys[counter])[0]
            word = dict_keys[counter]

            say_text("Question {}, {}".format(str(counter + 1), definition), robot)

            while not correct:
                text = get_text_from_audio()

                # If the user answers, then check if the answer is correct
                if text:

                    logger.info(text)

                    # If the try_again_flag is set, make user stuck in the first part of the loop until he says yes or no
                    if try_again_flag:

                        logger.info("User answering try_again...")

                        # Add long string of confirmation and denial words
                        if check_answer_list(text, confirmation_words):
                            try_again_flag = False
                            say_text("Question {}, {}".format(str(counter + 1), definition), robot)

                        elif check_answer_list(text, denial_words):
                            try_again_flag = False
                            say_text("The word is {}.".format(word), robot)
                            say_text("It means {}".format(definition), robot)
                            break

                        continue

                    correct = check_answer(text.replace(" ", ""), word.replace(" ", ""))

                    if correct:
                        logger.info("Correct answer: {} {}".format(text, word))
                        say_text("Your answer {}.".format(text), robot)
                        say_text("is", robot)
                        say_text("Correct! Good Job!", robot)
                        number = random.randint(0, 9)
                        logger.info("Good animation number " + str(number))
                        robot.play_anim_trigger(
                            robot.anim_triggers[good_animations[number]],
                            in_parallel=True, ignore_body_track=True).wait_for_completed()
                        robot.set_head_angle(cozmo.robot.MAX_HEAD_ANGLE, in_parallel=True).wait_for_completed()
                    else:
                        logger.info("Incorrect answer: {} {}".format(text, word))
                        first_try = False
                        say_text("Your answer {}, is not correct".format(text), robot)
                        number = random.randint(0, 9)
                        logger.info("Bad animation number " + str(number))
                        robot.play_anim_trigger(
                            robot.anim_triggers[bad_animations[random.randint(0, 9)]],
                            in_parallel=True, ignore_body_track=True).wait_for_completed()
                        robot.set_head_angle(cozmo.robot.MAX_HEAD_ANGLE, in_parallel=True).wait_for_completed()
                        try_again_flag = True
                        say_text("Would you like to try again?", robot)

            if first_try:
                first_try_counter += 1

            counter += 1

        stream.stop_stream()
        logger.info("End of vocabulary exercise...")
        logger.info("Start of vocabulary exercise summary...")
        score = first_try_counter / dict_length
        percentage = score * 100
        percentage = round(percentage, 2)

        logger.info("{} = {}/{}".format(float(percentage), int(dict_length), int(first_try_counter)))

        say_text("I would like to say, first of all, great job, {}".format(name), robot)
        say_text("Give me a nice fist bump!", robot)
        logger.info("Starting fist bump...")
        fist_bump(robot)
        logger.info("Ending fist bump...")
        say_text("You got {} correct answers out of {} questions. That is a {} percentage.".format(first_try_counter,
                                                                                                   dict_length,
                                                                                                   percentage), robot)

        if percentage >= 90:
            say_text("Fantastic job! I'm impressed!", robot)
        elif percentage >= 70:
            say_text("Good job! That was good!", robot)
        elif percentage >= 50:
            say_text("You are getting there. Don't give up and let's keep practicing!", robot)
        else:
            say_text(
                "It's not that easy, but I'm glad that you are trying, don't give up and let's practice again next "
                "time!", robot)

        robot.play_anim_trigger(
            robot.anim_triggers[good_animations[random.randint(0, 9)]],
            in_parallel=True, ignore_body_track=True).wait_for_completed()

        logger.info("End of vocabulary exercise summary...")
        # -------------End of definition quiz------------------
        say_text(
            "We are now done with the vocabulary training. Please say, okay, to continue to the dialogue training.",
            robot)

        logger.info("Waiting for user confirmation word...")

        stream.start_stream()
        while True:
            text = get_text_from_audio()

            if text:
                logger.info("Confirmation word: " + text)
                word_said = check_answer_list(text, ["okay", "ok"])

                if word_said:
                    break

        stream.stop_stream()
        logger.info("Confirmation word accepted...")
        # ------------Beginning of dialogue training--------------

        logger.info("Starting dialogue exercise...")

        say_text("We will now practice dialogue. This will be a telephone call.", robot)
        say_text(
            "You are a secretary of Mr. Franks. Mr. Franks is out of town so he is not available to talk on the telephone.",
            robot)
        say_text("Cozmo is calling to complain about the problem and will ask for Mr. Franks.", robot)
        say_text("Mr. Franks did not tell you any details of this problem so you should ask what the problem is.",
                 robot)
        say_text("Cozmo will ask for a meeting with Mr. Franks on Thursday afternoon.", robot)
        say_text(
            "Mr. Franks is busy in the afternoon but you can offer Cozmo a meeting slot with Mr. Franks on Thursday morning.",
            robot)
        say_text("Thursday morning does not work for Cozmo and you see that Mr. Franks is available on Friday morning",
                 robot)
        say_text("Mr. Franks is available only from 10 in the morning on Friday.", robot)
        say_text("So your role as a secretary is to ", robot)
        say_text("First, tell Cozmo Mr. Franks is not available.", robot)
        say_text("Second, ask Cozmo about the details of the problem.", robot)
        say_text(
            "Third, tell Cozmo that Mr. Franks is not available on Thursday afternoon but Thursday or Friday morning works for a meeting.",
            robot)
        say_text("Finally, tell Cozmo that Mr. Franks is available at 10 in the morning on Friday.", robot)
        say_text("And, do not forget to ask if Cozmo needs anything else.", robot)
        say_text("During the dialog training, please speak in full sentences!", robot)
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

        logger.info("Entering talking loop...")
        stream.start_stream()
        for line in lines:
            logger.info(line)
            say_text(line, robot)

            timeout = 10  # [seconds]
            timeout_start = time.time()  # [seconds]

            while time.time() < timeout_start + timeout:
                data = stream.read(4096, exception_on_overflow=False)

                text = recognizer.PartialResult()[17:-3]

                if text:
                    logger.info(text)
                    timeout_start = time.time()
                    timeout = 3

                if recognizer.AcceptWaveform(data):
                    sentence = recognizer.Result()[14:-3]

        stream.stop_stream()
        logger.info("Exiting talking loop...")
        logger.info("Ending dialogue exercise...")
        say_text("This is the end of the dialogue training.", robot)

        logger.info("End of study dialogue...")

        say_text("Thank you for participating in the study, you helped me learn more about humans, and I hope you had "
                 "fun. Give me one last fist bump!", robot)
        fist_bump(robot)
        say_text("Thank youuuu, goodbye!", robot)
        robot.play_anim_trigger(
            robot.anim_triggers[213],
            in_parallel=True, ignore_body_track=True).wait_for_completed()

    except Exception as e:
        logger.critical(e, exc_info=True)


def main(robot: cozmo.robot.Robot):
    cozmo.robot.Robot.drive_off_charger_on_connect = False
    t1 = threading.Thread(target=cozmo_program, args=(robot,))
    t2 = threading.Thread(target=follow_face, args=(robot, condition))
    logger.info("Thread 1 started...")
    logger.info("Thread 2 started...")
    t1.start()
    t2.start()
    t1.join()
    logger.info("Thread 1 finished...")
    condition.set()
    t2.join()
    logger.info("Thread 2 finished...")
    logger.info("Shutting down...")


if __name__ == "__main__":
    cozmo.run_program(main)

# TODO: Potential feature: "I might not understand this word. Do you want to type it with a keyboard?"
# TODO: Maybe this whole idea could work with cubes. Press on a cube to move on, maybe to repeat the definition again (AFTER PROTOTYPE)
