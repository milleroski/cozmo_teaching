# TODO: Make threading a seperate file
# import threading
# from base_logger import logger
#
# def threading(t1_name):
#     condition = threading.Event()
#     cozmo.robot.Robot.drive_off_charger_on_connect = False
#     t1 = threading.Thread(target=cozmo_program, args=(robot,))
#     t2 = threading.Thread(target=follow_face, args=(robot, condition,))
#     logger.info("Thread 1 started...")
#     logger.info("Thread 2 started...")
#     t1.start()
#     t2.start()
#     t1.join()
#     logger.info("Thread 1 finished...")
#     condition.set()
#     t2.join()
#     logger.info("Thread 2 finished...")
#     logger.info("Shutting down...")