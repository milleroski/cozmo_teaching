import logging
import datetime
import os

logger = logging

file_directory = os.path.dirname(__file__)
logging_directory = os.path.join(file_directory, '../logging/')
currentDT = datetime.datetime.now()
FileName = logging_directory + currentDT.strftime("%Y_%m_%d_%H_%M_%S") + "_cozmo_english.log"
logging.basicConfig(
    filename=FileName,
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.DEBUG,
    datefmt='%Y-%m-%d %H:%M:%S')
