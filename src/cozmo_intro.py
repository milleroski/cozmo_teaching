import cozmo
import time
from cozmo.util import degrees, distance_mm, speed_mmps

# TODO: Plan --


def cozmo_program(robot: cozmo.robot.Robot):
    #robot.lift_angle(0)
    robot.set_lift_height(1).wait_for_completed()
    robot.set_robot_volume(1)
    robot.drive_straight(distance_mm(250), speed_mmps(200)).wait_for_completed()
    robot.play_anim_trigger(cozmo.anim.Triggers.FrustratedByFailure, ignore_body_track=True).wait_for_completed()
    robot.drive_straight(distance_mm(-50), speed_mmps(50)).wait_for_completed()
    robot.turn_in_place(degrees(90)).wait_for_completed()
    robot.play_anim_trigger(cozmo.anim.Triggers.ConnectWakeUp, ignore_body_track=True).wait_for_completed()
    robot.play_anim_trigger(cozmo.anim.Triggers.MajorWin, ignore_body_track=True).wait_for_completed()
    # robot.say_text("Hi! I'm Cozmo! Your friendly language companion!", play_excited_animation=True, duration_scalar=0.8).wait_for_completed()
    # robot.say_text("I am trying to understand how people learn.", play_excited_animation=True, duration_scalar=0.7).wait_for_completed()
    # robot.say_text("and therefore, I'd like for YOU to participate in a study with me!", play_excited_animation=True, duration_scalar=0.7).wait_for_completed()
    # robot.say_text("We will be practicing English and German vocabulary and dialogue, and I will be giving you personal feedback!", play_excited_animation=True, duration_scalar=0.7).wait_for_completed()
    # robot.say_text("I hope to see you there!", play_excited_animation=True, duration_scalar=0.7).wait_for_completed()
    robot.say_text("Hi! Ich bin Cozmo! Dein Sprachlernpartner!", play_excited_animation=True, duration_scalar=0.8).wait_for_completed()
    robot.say_text("Ich will verstehen, wie Menschen lernen.", play_excited_animation=True, duration_scalar=0.7).wait_for_completed()
    robot.say_text("Und DU kannst mir dabei helfen!", play_excited_animation=True, duration_scalar=0.7).wait_for_completed()
    robot.say_text("Wir werden Deutsches und Englisches Vokabular und Dialog üben, und ICH werde dir persönliches Feedback geben!", play_excited_animation=True, duration_scalar=0.7).wait_for_completed()
    robot.say_text("Ich hoffe wir sehen uns da!", play_excited_animation=True, duration_scalar=0.7).wait_for_completed()
    robot.drive_straight(distance_mm(-50), speed_mmps(300)).wait_for_completed()
    robot.turn_in_place(degrees(-90)).wait_for_completed()
    robot.drive_straight(distance_mm(250), speed_mmps(300)).wait_for_completed()

cozmo.robot.Robot.drive_off_charger_on_connect = False
cozmo.run_program(cozmo_program)
