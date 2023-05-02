import cozmo
from cozmo.util import degrees
import asyncio
import cozmo.faces
import time
from base_logger import logger

def handle_face_observed(evt, face: cozmo.faces.Face, **kwargs):
    logger.info(face.expression + "-" + str(face.expression_score))


def follow_face(robot: cozmo.robot.Robot, condition):

    robot.enable_facial_expression_estimation()
    logger.info("Following face...")
    face_to_follow = None
    while not condition:
        time.sleep(0.5)
        turn_action = None
        if face_to_follow:
            # Log the facial recognition...start turning towards the face
            robot.add_event_handler(cozmo.faces.EvtFaceObserved, handle_face_observed)
            # ... but only once per loop (without the oneshot it prints the result every FRAME
            cozmo.event.oneshot(handle_face_observed)

            # turn towards the face if the fist bump animation is not taking place
            if robot.lift_ratio < 0.75: #dependency on other function
                turn_action = robot.turn_towards_face(face_to_follow, in_parallel=True)

        if not (face_to_follow and face_to_follow.is_visible):
            logger.info("Lost face, searching...")

            # find a visible face, timeout if nothing found after a short while
            try:
                face_to_follow = robot.world.wait_for_observed_face(timeout=1)
            except asyncio.TimeoutError:
                if robot.lift_ratio < 0.75: #dependency on other function
                    turn_action = robot.turn_in_place(degrees(45), in_parallel=True)
                face_to_follow = None

        if turn_action:
            # Complete the turn action if one was in progress
            turn_action.wait_for_completed()
