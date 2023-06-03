import cozmo
import random
import time
from src.utils import say_text
from src.base_logger import logger

# Lists of good, bad, and neutral animations
bad_animations = [63, 65]
good_animations = [1, 7, 23, 26, 30, 31, 35, 50, 57, 68]
listening_animations = [2, 3, 7, 18, 22]


def play_random_bad_animation(robot: cozmo.robot.Robot):

    number = random.randint(0, 1)
    logger.info("Bad animation number " + str(number))

    robot.play_anim_trigger(
        robot.anim_triggers[bad_animations[number]],
        in_parallel=True, ignore_body_track=True).wait_for_completed()
    robot.set_head_angle(cozmo.robot.MAX_HEAD_ANGLE, in_parallel=True).wait_for_completed()


def play_random_good_animation(robot: cozmo.robot.Robot):
    number = random.randint(0, 9)
    logger.info("ANIM: Good animation number " + str(number))
    robot.play_anim_trigger(
        robot.anim_triggers[good_animations[number]],
        in_parallel=True, ignore_body_track=True).wait_for_completed()
    robot.set_head_angle(cozmo.robot.MAX_HEAD_ANGLE, in_parallel=True).wait_for_completed()


def play_random_listening_animation(robot: cozmo.robot.Robot):
    number = random.randint(0, 2)
    logger.info("Listening animation number " + str(number))
    robot.play_anim_trigger(
        robot.anim_triggers[listening_animations[number]],
        in_parallel=True, ignore_head_track=True).wait_for_completed()


def sense_bump(robot: cozmo.robot.Robot, save_acc):
    sensibility = 1000
    if save_acc._x > robot.accelerometer._x + sensibility or save_acc._x < robot.accelerometer._x - sensibility:
        return True
    if save_acc._y > robot.accelerometer._y + sensibility or save_acc._y < robot.accelerometer._y - sensibility:
        return True
    if save_acc._z > robot.accelerometer._z + sensibility or save_acc._z < robot.accelerometer._z - sensibility:
        return True
    return False


def fist_bump(robot: cozmo.robot.Robot):
    logger.info("ANIM: In fist_bump")
    print("doing animation")
    robot.play_anim_trigger(robot.anim_triggers[199], in_parallel=True, ignore_body_track=True,
                            ignore_head_track=True).wait_for_completed()
    save_acc = robot.accelerometer
    logger.info("ANIM: Entering first bump loop...")

    timeout = 5  # [seconds]
    timeout_start = time.time()  # [seconds]

    while not sense_bump(robot, save_acc):
        print("ANIM: In fist_bump loop")

        # If 8 seconds pass, repeat give me a fist bump
        if time.time() >= timeout_start + timeout:
            say_text("Give me a fist bump!", robot)
            timeout_start = time.time()

    logger.info("ANIM: Exiting first bump loop...")
    robot.play_anim_trigger(robot.anim_triggers[201], in_parallel=True, ignore_body_track=True,
                            ignore_head_track=True).wait_for_completed()
    robot.set_head_angle(cozmo.robot.MAX_HEAD_ANGLE, in_parallel=True).wait_for_completed()
    robot.set_lift_height(0, in_parallel=True)


def main(robot: cozmo.robot.Robot):
    epic = "epic"


if __name__ == "__main__":
    cozmo.run_program(main)
