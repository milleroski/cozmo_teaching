import cozmo
from src.base_logger import logger
from src.english.cozmo_vocabulary import cozmo_vocabulary
from src.english.cozmo_transition import cozmo_transition
from src.english.cozmo_dialogue import cozmo_dialogue
from src.animations import fist_bump
from src.utils import say_text
from src.threads import start_threads


def cozmo_program(robot: cozmo.robot.Robot):
    # Move Cozmo's head up and the lift down
    try:
        cozmo_vocabulary(robot)
        cozmo_transition(robot)
        cozmo_dialogue(robot)
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
    start_threads(robot, cozmo_program)


if __name__ == "__main__":
    cozmo.run_program(main)

# TODO: Potential feature: "I might not understand this word. Do you want to type it with a keyboard?"
# TODO: Maybe this whole idea could work with cubes. Press on a cube to move on, maybe to repeat the definition again (AFTER PROTOTYPE)
