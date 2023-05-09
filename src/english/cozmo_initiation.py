import cozmo
from src.base_logger import logger
from src.speech_detection import get_text_from_audio, stream, confirmation_words, denial_words
from src.utils import say_text, check_answer_list
from src.animations import fist_bump
from src.threads import start_threads


# This file initiates everything necessary for Cozmo to run the exercises

def get_name(robot: cozmo.robot.Robot):
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
    return name


def cozmo_initiation(robot: cozmo.robot.Robot):
    try:
        robot.set_robot_volume(0.1)
        logger.info("Preparation started...")
        logger.info("current battery voltage: " + str(robot.battery_voltage) + "V")

        robot.set_head_angle(cozmo.robot.MAX_HEAD_ANGLE, in_parallel=True).wait_for_completed()
        robot.set_lift_height(0, in_parallel=True)

        logger.info("Preparation ended...")
        # -------------Initiation and name-----------------------
        logger.info("Start of introduction...")
        say_text("Hi there! I'm Cozmo! Your language learning companion!", robot)
        say_text("You can interact with me through the microphone when I ask questions!", robot)
        say_text(
            "Please try to give me clear answers if possible, and repeat your answer if I do not respond to you, "
            "as I'm still learning how to interact with humans!",
            robot)

        name = get_name(robot)
        say_text("Ok, {}, Give me a nice fist bump!".format(name), robot)

        logger.info("Starting fist bump...")
        fist_bump(robot)
        logger.info("Ending fist bump...")

        logger.info("End of introduction...")

        return name

    except Exception as e:
        logger.critical(e)


def main(robot: cozmo.robot.Robot):
    # This condition is used to stop the thread looping in follow_face
    start_threads(robot, cozmo_initiation)

if __name__ == "__main__":
    cozmo.run_program(main)
