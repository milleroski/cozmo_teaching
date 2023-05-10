from src.utils import say_text, check_answer_list
from src.speech_detection import stream
from src.base_logger import logger
from src.cubes import press_cube_to_speak


def cozmo_transition(robot):
    say_text(
        "We are now done with the vocabulary training. Please say, okay, to continue to the dialogue training.",
        robot)

    logger.info("Waiting for user confirmation word...")

    stream.start_stream()
    while True:
        text = press_cube_to_speak(robot)

        if text:
            logger.info("Confirmation word: " + text)
            word_said = check_answer_list(text, ["okay", "ok"])

            if word_said:
                break

    stream.stop_stream()
    logger.info("Confirmation word accepted...")