import cozmo
from src.base_logger import logger
from src.speech_detection import get_text_from_audio


def press_cube_to_speak(robot: cozmo.robot.Robot):

    cube = robot.world.get_light_cube(1)

    if cube:

        logger.info("CUBE: light is green")
        cube.set_lights(cozmo.lights.green_light)

        if cube.wait_for_tap():
            logger.info("CUBE: has been tapped")

            logger.info("CUBE: light is blue")
            cube.set_lights(cozmo.lights.blue_light)

            while True:
                text = get_text_from_audio()

                if text:
                    logger.info("CUBE: light is red")
                    cube.set_lights(cozmo.lights.red_light)
                    return text


def main(robot: cozmo.robot.Robot):
    press_cube_to_speak(robot)


if __name__ == "__main__":
    cozmo.robot.Robot.drive_off_charger_on_connect = False
    cozmo.run_program(main)
