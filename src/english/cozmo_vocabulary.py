import cozmo
from src.base_logger import logger
from src.speech_detection import stream
from src.utils import say_text, check_answer, check_answer_list
from src.speech_detection import confirmation_words, denial_words
from src.animations import play_random_good_animation, play_random_bad_animation, fist_bump
from DictionaryEnglish import load_dictionary
from cozmo_initiation import cozmo_initiation
from src.threads import start_threads
from src.cubes import press_cube_to_speak

# Global variables relevant to all functions
name = ""
dictionary = load_dictionary()
dict_keys = list(dictionary.keys())
dict_length = len(dictionary)


def definition_exercise(robot):

    logger.info("Start of vocabulary exercise...")
    # Initiate the dictionary and get the definitions + the length
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
            text = press_cube_to_speak(robot)

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
                    say_text("Your answer {}. Is correct, good job!".format(text), robot)
                    play_random_good_animation(robot)
                else:
                    logger.info("Incorrect answer: {} {}".format(text, word))
                    first_try = False
                    say_text("Your answer {}, is not correct".format(text), robot)
                    play_random_bad_animation(robot)
                    try_again_flag = True
                    say_text("Would you like to try again?", robot)

        if first_try:
            first_try_counter += 1

        counter += 1
    stream.stop_stream()
    logger.info("End of vocabulary exercise...")
    return first_try_counter


def exercise_summary(first_try_counter, robot):
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
    play_random_good_animation(robot)
    logger.info("End of vocabulary exercise summary...")


def cozmo_vocabulary(robot: cozmo.robot.Robot):
    try:
        global name
        name = cozmo_initiation(robot)

        first_try_counter = definition_exercise(robot)
        exercise_summary(first_try_counter, robot)

    except Exception as e:
        logger.critical(e, exc_info=True)


def main(robot: cozmo.robot.Robot):
    # This condition is used to stop the thread looping in follow_face
    start_threads(robot, cozmo_vocabulary)


if __name__ == "__main__":
    cozmo.run_program(main)
