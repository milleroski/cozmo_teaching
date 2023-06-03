import cozmo
import time
import os
from src.threads import start_threads
from src.base_logger import logger
from src.utils import say_text
from src.speech_detection import stream, recognizer


def load_lines():
    lines = []

    # Read the text file and write it into list, also, get rid of unnecessary lines
    with open(os.path.abspath("../../text_files/EnglishDialogue.txt"), encoding='utf8') as _:
        for line in _:
            line = line.strip()
            if line:
                lines.append(line)

    return lines


def exercise_explanation(robot):
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


def dialogue_recognizer(lines, robot):
    cube = robot.world.get_light_cube(1)

    logger.info("Entering talking loop...")
    stream.start_stream()
    for line in lines:
        logger.info(line)
        cube.set_lights(cozmo.lights.red_light)
        say_text(line, robot)
        cube.set_lights(cozmo.lights.green_light)

        timeout = 10  # [seconds]
        timeout_start = time.time()  # [seconds]

        while time.time() < timeout_start + timeout:
            data = stream.read(4096, exception_on_overflow=False)

            text = recognizer.PartialResult()[17:-3]

            if text:
                cube.set_lights(cozmo.lights.blue_light)
                logger.info(text)
                timeout_start = time.time()
                timeout = 1

            if recognizer.AcceptWaveform(data):
                sentence = recognizer.Result()[14:-3]

    cube.set_lights(cozmo.lights.red_light)
    stream.stop_stream()
    logger.info("Exiting talking loop...")


def cozmo_dialogue(robot: cozmo.robot.Robot):
    try:
        logger.info("Starting dialogue exercise...")

        exercise_explanation(robot)

        lines = load_lines()

        dialogue_recognizer(lines, robot)
        logger.info("Ending dialogue exercise...")
        say_text("This is the end of the dialogue training.", robot)

    except Exception as e:
        logger.critical(e, exc_info=True)


def main(robot: cozmo.robot.Robot):
    start_threads(robot, cozmo_dialogue)


if __name__ == "__main__":
    cozmo.run_program(main)
