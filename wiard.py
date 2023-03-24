import os
import logging

def get_log_file(file):
  logfile = '.'.join([os.path.splitext(file)[0], 'log'])
  if os.getenv('DEBUG'):
    logging.basicConfig(filename = logfile, filemode = 'w', level = logging.DEBUG)
  else:
    logging.basicConfig(filename = logfile, filemode = 'w', level = logging.INFO)
