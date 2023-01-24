#!/usr/bin/env python3

import os
import sys
import logging

import ffmpeg

from pathlib import Path
from pprint import pprint

import wiard

from audiofile import AudioFile
from tagit-spotify import TagitSpotify


#
# 1. [done] get artist and title from filename and parent directory
# 2. get data from airtable
# 3. get data from spotify
# 4. get lyrics from azlyrics
# 5. convert file to opus, if needed
# 6. delete any existing metadata from opus file
# 7. add metadata to opus file
# 8. add replaygain tags to opus file
# 9. rename file, if needed
#



def get_audio_fileset(fileset):
  result = []

  if len(fileset) > 0:
    for f in fileset:
      audiofile = AudioFile(os.path.join(os.getcwd(), f))
      result.append(audiofile)

    return result

  for (dir, _, files) in os.walk(os.getcwd()):
    for f in files:
      if is_matching_file_type(os.path.join(dir, f), [AudioFile._TYPE_MP3, AudioFile._TYPE_OGG_OPUS, AudioFile._TYPE_OGG_VORBIS]):
        audiofile = AudioFile(os.path.join(dir, f))
        result.append(audiofile)

  return result


def get_output_filename(input_audiofile, filename):
  if input_audiofile.type == AudioFile._TYPE_MP3:
    return filename.replace(AudioFile._EXT_MP3, AudioFile._EXT_OGG_OPUS)
  elif input_audiofile.type == AudioFile._TYPE_OGG_VORBIS:
    return filename.replace(AudioFile._EXT_OGG_VORBIS, AudioFile._EXT_OGG_OPUS)
  elif input_audiofile.type == AudioFile._TYPE_OGG_OPUS:
    return filename


def is_matching_file_type(filename, codecs):
  try:
    stream = ffmpeg.probe(filename)['streams'][0]
  except:
    return False

  codec = stream['codec_name']
  if codec in codecs:
    return True
  else:
    return False








if __name__  == '__main__':
  wiard.get_log_file(__file__)

  audio_files_to_process = get_audio_fileset(sys.argv[1:])

  for input_audiofile in audio_files_to_process:
    logging.debug('audio file to process: %s' % input_audiofile.filename)

    title = Path(input_audiofile.filename).stem
    artist = Path(input_audiofile.filename).parent.stem

    spotify_data = TagitSpotify(artist, title)
    pprint(spotify_data)
