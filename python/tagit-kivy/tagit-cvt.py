#!/usr/bin/env python3

from pathlib import Path
import sys
import ffmpeg
import logging

def convert_file_type(input_filename, output_filename):
  print('----')
  print(input_filename)
  print('----')
  print(output_filename)
  print('----')
  logging.debug('Converting "' + input_filename +  '" to "' + output_filename + '"')
  try:
    ffmpeg                                                  \
      .input(input_filename)                                \
      .output(output_filename, **{'acodec':  'libopus'})    \
      .overwrite_output()                                   \
      .run()
  except Exception as err:
    print(f"Unexpected {err=}, {type(err)=}")
    raise


if __name__ == '__main__':
  input_filename = sys.argv[1]
  if input_filename.endswith('.opus'):
    print('Not converting an opus file to opus format')

  output_filename = '.'.join([Path(input_filename).stem, 'opus'])
  convert_file_type(input_filename, output_filename)
