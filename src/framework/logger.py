import logging
import os
from datetime import datetime

# create logger with 'spam_application'
logger = logging.getLogger('hots_bot')
logger.setLevel(logging.DEBUG)

# create file handler which logs even debug messages
logs_dir = 'logs'
if not os.path.exists(logs_dir):
    os.makedirs(logs_dir)
log_file_name = datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + '.log'
log_path = os.path.join(logs_dir, log_file_name)
fh = logging.FileHandler(log_path)
fh.setLevel(logging.DEBUG)

# create console handler with a higher log level
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)

# create formatter and add it to the handlers
formatter = logging.Formatter('%(levelname)s - %(asctime)s - %(name)s - %(message)s')
fh.setFormatter(formatter)
ch.setFormatter(formatter)

# add the handlers to the logger
logger.addHandler(fh)
logger.addHandler(ch)
