#!/usr/bin/env python3

import os
import sys
import logging

from pathlib import Path
from fontTools.ttLib import TTFont


if __name__ == '__main__':
  logfile = '.'.join([os.path.splitext(__file__)[0], 'log'])
  if os.getenv('DEBUG'):
    logging.basicConfig(filename = logfile, filemode = 'w', level = logging.DEBUG)
  else:
    logging.basicConfig(filename = logfile, filemode = 'w', level = logging.INFO)

  for filename in sys.argv[1:]:
    print(filename)
    
    font = TTFont(filename)
    family = font['name'].getBestFamilyName()
    type = Path(filename).suffix
    if filename != ''.join([family, type]):
      print('Renaming "' + filename + '" to "' + ''.join([family, type]) + '"')
      os.rename(filename, ''.join([family, type]))
    else:
      print('File already named correctly')