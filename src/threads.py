import threading
from src.base_logger import logger
from src.face_detection import follow_face


def start_threads(robot, t1_name):
    condition = threading.Event()
    t1 = threading.Thread(target=t1_name, args=(robot,))
    t2 = threading.Thread(target=follow_face, args=(robot, condition,))
    logger.info("Thread 1 started...")
    logger.info("Thread 2 started...")
    t1.start()
    t2.start()
    t1.join()
    logger.info("Thread 1 finished...")
    condition.set()
    t2.join()
    logger.info("Thread 2 finished...")
    logger.info("Shutting down...")