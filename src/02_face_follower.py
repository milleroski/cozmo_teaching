#!/usr/bin/env python3

# Copyright (c) 2016 Anki, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License in the file LICENSE.txt or at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import asyncio
import threading
import cozmo.faces
import random
import time
from cozmo.util import degrees


def baba(robot):
    good_animations = [1, 7, 23, 26, 30, 31, 35, 50, 57, 68]
    robot.set_robot_volume(0.1)
    while True:
        print("Doing animation...")
        robot.say_text("blah blah blah blah", in_parallel=True).wait_for_completed()


# This function is called whenever Cozmo is not doing anything else, it just follows a users face
def follow_face(robot):
    print("Following face...")
    face_to_follow = None
    while True:
        print("in here")
        #time.sleep(2)
        turn_action = None
        if face_to_follow:
            # start turning towards the face
            # print(cozmo.faces.Face.expression)
            turn_action = robot.turn_towards_face(face_to_follow, in_parallel=True)
        if not (face_to_follow and face_to_follow.is_visible):
            # find a visible face, timeout if nothing found after a short while
            try:
                face_to_follow = robot.world.wait_for_observed_face(timeout=1)
            except asyncio.TimeoutError:
                turn_action = robot.turn_in_place(degrees(45), in_parallel=True)
                face_to_follow = None

        if turn_action:
            # Complete the turn action if one was in progress
            turn_action.wait_for_completed()

def run_action(lock, robot):
    with lock:
        print("babagee")



def main(robot: cozmo.robot.Robot):
    robot.set_head_angle(cozmo.robot.MAX_HEAD_ANGLE).wait_for_completed()
    lock = threading.Lock()
    t1 = threading.Thread(target=baba, args=(robot,))
    t2 = threading.Thread(target=follow_face, args=(robot,))
    t1.start()
    t2.start()
    t1.join()
    t2.join()

cozmo.run_program(main)
