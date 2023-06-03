import cozmo
import os
import random
from src.base_logger import logger


# Function that takes a list of common english words and picks three out of the list at random.
def three_random_words():
    file_directory = os.path.dirname(__file__)
    word_directory = os.path.join(file_directory, '../text_files/common_words.txt')

    words = []
    with open(word_directory, encoding='utf8') as _:
        for line in _:
            line = line.strip()
            if line:
                words.append(line)

    picked_words = random.sample(words, 3)
    return picked_words


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
    logger.info("UTILS: Saying text: " + text)
    robot.say_text(text, duration_scalar=0.7, in_parallel=True).wait_for_completed()
