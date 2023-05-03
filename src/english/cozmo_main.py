import cozmo
import cozmo.faces
import threading
from src.base_logger import logger
from src.face_detection import follow_face
from cozmo_vocabulary import cozmo_vocabulary
from cozmo_transition import cozmo_transition
from cozmo_dialogue import cozmo_dialogue
from src.animations import fist_bump
from src.utils import say_text


def cozmo_program(robot: cozmo.robot.Robot):
    # Move Cozmo's head up and the lift down
    try:
        # cozmo_vocabulary(robot)
        # cozmo_transition(robot)
        # cozmo_dialogue(robot)
        # say_text("Thank you for participating in the study, you helped me learn more about humans, and I hope you had "
        #          "fun. Give me one last fist bump!", robot)
        # fist_bump(robot)
        say_text("Thank youuuu, goodbye!", robot)
        robot.play_anim_trigger(
            robot.anim_triggers[213],
            in_parallel=True, ignore_body_track=True).wait_for_completed()

    except Exception as e:
        logger.critical(e, exc_info=True)


def main(robot: cozmo.robot.Robot):
    # This condition is used to stop the thread looping in follow_face
    condition = threading.Event()
    cozmo.robot.Robot.drive_off_charger_on_connect = False
    t1 = threading.Thread(target=cozmo_program, args=(robot,))
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

# TODO: Potential feature: "I might not understand this word. Do you want to type it with a keyboard?"
# TODO: Maybe this whole idea could work with cubes. Press on a cube to move on, maybe to repeat the definition again (AFTER PROTOTYPE)
