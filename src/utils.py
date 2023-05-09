import cozmo
from src.base_logger import logger


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
