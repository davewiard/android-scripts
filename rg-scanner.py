#!/usr/bin//env python3

import os
import sys
import logging
import ffmpeg


def get_fileset(fileset):
  result = []
  if len(fileset) < 1:
    with os.scandir('.') as entries:
      for entry in entries:
        if os.path.isfile(entry.name):
          print(entry.name)
          result.append(entry.name)
  else:
    result = fileset
    
  return result
        

if __name__ == '__main__':
  if os.getenv('DEBUG'):
    logging.basicConfig(filename='rg-scanner.log', filemode='w', level=logging.DEBUG)
  else:
    logging.basicConfig(filename='rg-scanner.log', filemode='w', level=logging.INFO)

  fileset = sys.argv[1:]
  print(fileset)
  
  files_to_process = get_fileset(sys.argv[1:])

  # ffmpeg.probe('./a.opus'))['streams'][0]['codec_name']