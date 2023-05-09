import cozmo
import random
from src.base_logger import logger

# Lists of good, bad, and neutral animations
bad_animations = [4, 5, 17, 21, 25, 27, 54, 63, 64, 65]
neutral_animations = [3, 18, 22, 40, 51, 58, 61, 77, 78, 80]
good_animations = [1, 7, 23, 26, 30, 31, 35, 50, 57, 68]


def play_random_bad_animation(robot: cozmo.robot.Robot):
    number = random.randint(0, 9)
    logger.info("Bad animation number " + str(number))
    robot.play_anim_trigger(
        robot.anim_triggers[bad_animations[random.randint(0, 9)]],
        in_parallel=True, ignore_body_track=True).wait_for_completed()
    robot.set_head_angle(cozmo.robot.MAX_HEAD_ANGLE, in_parallel=True).wait_for_completed()


def play_random_good_animation(robot: cozmo.robot.Robot):
    number = random.randint(0, 9)
    logger.info("Good animation number " + str(number))
    robot.play_anim_trigger(
        robot.anim_triggers[good_animations[number]],
        in_parallel=True, ignore_body_track=True).wait_for_completed()
    robot.set_head_angle(cozmo.robot.MAX_HEAD_ANGLE, in_parallel=True).wait_for_completed()


def sense_bump(robot: cozmo.robot.Robot, save_acc):
    sensibility = 1000
    if save_acc._x > robot.accelerometer._x + sensibility or save_acc._x < robot.accelerometer._x - sensibility:
        return True
    if save_acc._y > robot.accelerometer._y + sensibility or save_acc._y < robot.accelerometer._y - sensibility:
        return True
    if save_acc._z > robot.accelerometer._z + sensibility or save_acc._z < robot.accelerometer._z - sensibility:
        return True
    return False


# Code taken from animation.py, written by Maximilian
def fist_bump(robot: cozmo.robot.Robot):
    logger.info("In fist bump")
    robot.play_anim_trigger(robot.anim_triggers[199], in_parallel=True, ignore_body_track=True,
                            ignore_head_track=True).wait_for_completed()
    save_acc = robot.accelerometer
    logger.info("Entering first bump loop...")

    while not sense_bump(robot, save_acc):
        print("In fist_bump loop")
        # If 3 seconds pass, repeat give me a fist bump
    logger.info("Exiting first bump loop...")
    robot.play_anim_trigger(robot.anim_triggers[201], in_parallel=True, ignore_body_track=True,
                            ignore_head_track=True).wait_for_completed()
    robot.set_head_angle(cozmo.robot.MAX_HEAD_ANGLE, in_parallel=True).wait_for_completed()
    robot.set_lift_height(0, in_parallel=True)
