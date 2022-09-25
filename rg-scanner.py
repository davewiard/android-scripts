#!/usr/bin//env python3

import os
import sys
import logging
import ffmpeg
import subprocess
import pathlib


def fix_file_name(filename, stream):
  title = stream['tags']['TITLE']
  type = stream['codec_name']
    
  file = pathlib.Path(filename)
  if type == 'opus' and file.suffix != 'opus':
    if title:
      os.rename(filename, title + '.opus')
    else:
      os.rename(filename, file.stem + '.opus')
  elif type == 'vorbis' and file.suffix != 'ogg':
    if title:
      os.rename(filename, title + '.ogg')
    else:
      os.rename(filename, file.stem + '.ogg')
  elif type == 'mp3' and file.suffix != 'mp3':
    if title:
      os.rename(filename, title + '.mp3')
    else:
      os.rename(filename, file.stem + '.mp3')


def get_fileset(fileset):
  result = []
  if len(fileset) < 1:
    for (dir, _, files) in os.walk('.'):
      for f in files:
        result.append(os.path.join(dir, f))
  else:
    result = fileset

  return result


def process_one_file(filename):
  ret = None
  stream = ffmpeg.probe(filename)['streams'][0]
  codec = stream['codec_name']
  print(codec)
  if codec == 'opus':
    ret = process_opus_file(filename)
    if ret == 0:
      fix_file_name(filename, stream)
  elif codec == 'vorbis':
    ret = process_vorbis_file(filename)
    if ret == 0:
      fix_file_name(filename, stream)
  elif codec == 'mp3':
    ret = process_mp3_file(filename)
    if ret == 0:
      fix_file_name(filename, stream)
  else:
    pass # ignore, probably album art
    
  return ret


def process_opus_file(opus_file):
  # r128gain {}
  return (subprocess.run(['r128gain', opus_file])).returncode


def process_vorbis_file(vorbis_file):
  ret = (subprocess.run(['vorbisgain', '-c', vorbis_file])).returncode
  if ret != 0:
    return ret

  return (subprocess.run(['vorbisgain', '-q', '-a', '-n', vorbis_file])).returncode


def process_mp3_file(mp3_file):
  # mp3gain -s r -a {}
  return (subprocess.run(['mp3gain', '-s', 'r', '-a', mp3_file])).returncode


if __name__ == '__main__':
  logfile = os.path.join(os.getenv('HOME'), 'bin/rg-scanner.log')
  if os.getenv('DEBUG'):
    logging.basicConfig(filename=logfile, filemode='w', level=logging.DEBUG)
  else:
    logging.basicConfig(filename=logfile, filemode='w', level=logging.INFO)

  files_to_process = get_fileset(sys.argv[1:])
  for file_to_process in files_to_process:
    result = process_one_file(file_to_process)
    print('result = %s' % str(result))
