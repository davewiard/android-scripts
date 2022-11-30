#!/usr/bin/env python3

import os
import sys
import logging
import subprocess

import mutagen
import ffmpeg

from pathlib import Path
from tags import Tags

#
# 1. open mp3 file
# 2. read mp3 file tags
# 3. run ffmpeg to convert to libopus
# 4. add missing tags from mp3 file (lyrics, album art, etc.)
# 5. add ReplayGain tags
# 6. rename file, if needed
#




if __name__ == '__main__':
  logfile = '.'.join([os.path.splitext(__file__)[0], 'log'])
  if os.getenv('DEBUG'):
    logging.basicConfig(filename = logfile, filemode = 'w', level = logging.DEBUG)
  else:
    logging.basicConfig(filename = logfile, filemode = 'w', level = logging.INFO)

  audio_files_to_process = get_audio_fileset(sys.argv[1:])
  for audio_file_to_process in audio_files_to_process:
    print('audio_file_to_process: %s' %  audio_file_to_convert)
