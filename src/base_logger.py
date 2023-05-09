import logging
import datetime

logger = logging

currentDT = datetime.datetime.now()
FileName = currentDT.strftime("%Y_%m_%d_%H_%M_%S") + "_cozmo_english.log"

logging.basicConfig(
    filename=FileName,
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.DEBUG,
    datefmt='%Y-%m-%d %H:%M:%S')
