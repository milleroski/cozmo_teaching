import cozmo
from src.speech_detection import get_text_from_audio


def press_cube_to_speak(cube: cozmo.objects.LightCube):

    if cube:

        cube.set_lights(cozmo.lights.green_light)

        if cube.wait_for_tap():

            cube.set_lights(cozmo.lights.red_light)

            while True:
                text = get_text_from_audio()

                if text:
                    return text


def main(robot: cozmo.robot.Robot):
    cube = robot.world.get_light_cube(1)
    press_cube_to_speak(cube)


if __name__ == "__main__":
    cozmo.robot.Robot.drive_off_charger_on_connect = False
    cozmo.run_program(main)
