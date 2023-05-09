import cozmo
import time
import threading
from src.face_detection import follow_face
from src.base_logger import logger
from src.utils import say_text
from src.speech_detection import stream, recognizer


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


def cozmo_dialogue(robot: cozmo.robot.Robot):
    try:
        logger.info("Starting dialogue exercise...")

        exercise_explanation(robot)

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

        dialogue_recognizer(lines, robot)
        logger.info("Ending dialogue exercise...")
        say_text("This is the end of the dialogue training.", robot)

    except Exception as e:
        logger.critical(e, exc_info=True)

def main(robot: cozmo.robot.Robot):
    # This condition is used to stop the thread looping in follow_face
    condition = threading.Event()
    cozmo.robot.Robot.drive_off_charger_on_connect = False
    t1 = threading.Thread(target=cozmo_dialogue, args=(robot,))
    t2 = threading.Thread(target=follow_face, args=(robot, condition,))
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

