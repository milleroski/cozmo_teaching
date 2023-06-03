import cozmo
from src.base_logger import logger
from src.speech_detection import get_text_from_audio
from src.animations import play_random_listening_animation

cube = False

def init_cubes(robot: cozmo.robot.Robot):

    print(robot.world.connected_light_cubes)

    cube1 = robot.world.get_light_cube(1)
    cube2 = robot.world.get_light_cube(2)
    cube3 = robot.world.get_light_cube(3)

    if cube1:
        cube1.set_lights(cozmo.lights.red_light)
        return cube1
    elif cube2:
        cube2.set_lights(cozmo.lights.red_light)
        return cube2
    elif cube3:
        cube3.set_lights(cozmo.lights.red_light)
        return cube3
    else:
        return False

def press_cube_to_speak(robot: cozmo.robot.Robot):

    cube = robot.world.get_light_cube(3)

    if cube:

        logger.info("CUBE: light is green")
        cube.set_lights(cozmo.lights.green_light)

        if cube.wait_for_tap():
            logger.info("CUBE: has been tapped")

            play_random_listening_animation(robot)

            logger.info("CUBE: light is blue")
            cube.set_lights(cozmo.lights.blue_light)

            while True:
                text = get_text_from_audio()

                if text:
                    logger.info("CUBE: light is red")
                    cube.set_lights(cozmo.lights.red_light)
                    return text


def main(robot: cozmo.robot.Robot):
    # init_cubes(robot)
    press_cube_to_speak(robot)



if __name__ == "__main__":
    cozmo.robot.Robot.drive_off_charger_on_connect = False
    cozmo.run_program(main)

# TODO: Add proper cube initiation, you can't just assume that they're all going to be charged.
# TODO: Add backup in case cubes don't work at all (LIKE LITERALLY RIGHT NOW.)