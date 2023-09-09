#!/usr/bin/env python3

import os
import sys
import base64
import logging
import subprocess

import mutagen
import ffmpeg

from audiofile import AudioFile
from pathlib import Path
from tags import Tags


#
# 1. [done] get list of mp3 files to process
# 2. [done] open mp3 file
# 3. [done] read mp3 file tags
# 4. [done] run ffmpeg to convert to libopus
# 5. add missing tags from mp3 file (album art, etc.)
#    a. write mp3 cover image to disk
#    b. read disk cover image into METADATA_BLOCK_PICTURE tag
# 6. [done] add ReplayGain tags
# 7. [done] remove mp3 file if opus file exists
#


def add_replaygain_tags(filename):
  print('Applying ReplayGain tags...')
  process = subprocess.run(['r128gain', '-v', 'warning', filename])
  if process.returncode != 0:
    print('Failed to upsert ReplayGain tags')


def convert_to_opus(input_filename, output_filename):
  ffmpeg                                                  \
    .input(input_filename)                                \
    .output(output_filename, **{'acodec':  'libopus'})    \
    .overwrite_output()                                   \
    .run()


def get_audio_fileset(fileset):
  result = []
  
  if len(fileset) > 0:
    return fileset

  for (dir, _, files) in os.walk(os.getcwd()):
    for f in files:
      if is_matching_file_type(os.path.join(dir, f), [AudioFile._TYPE_MP3, AudioFile._TYPE_OGG_VORBIS]):
        result.append(os.path.join(dir, f))
  
  return result


def get_opus_filename(input_audiofile, filename):
  if input_audiofile.type == AudioFile._TYPE_MP3:
    return filename.replace(AudioFile._EXT_MP3, AudioFile._EXT_OGG_OPUS)
  elif input_audiofile.type == AudioFile._TYPE_OGG_VORBIS:
    return filename.replace(AudioFile._EXT_OGG_VORBIS, AudioFile._EXT_OGG_OPUS)


def is_matching_file_type(filename, codecs):
  stream = ffmpeg.probe(filename)['streams'][0]
  codec = stream['codec_name']
  if codec in codecs:
    return True
  else:
    return False


def remove_input_file(input_filename, output_filename):
  if Path(output_filename).exists():
    os.remove(input_filename)


def update_album_art(input_audiofile, output_audiofile):
  picture = mutagen.flac.Picture()
  picture.mime = AudioFile._MIME_IMAGE_JPEG
  picture.type = mutagen.id3.PictureType.COVER_FRONT
  
  if input_audiofile.type == AudioFile._TYPE_MP3:
    picture.data = input_audiofile.oldTags.album_art[0].data
    encoded_data = base64.b64encode(picture.write())
    metadata_block_picture = encoded_data.decode('ascii')

  elif input_audiofile.type == AudioFile._TYPE_OGG_VORBIS:
    metadata_block_picture = input_audiofile.oldTags.album_art[0]

  output_audiofile._mf['METADATA_BLOCK_PICTURE'] = metadata_block_picture
  output_audiofile._mf.save()
  

if __name__ == '__main__':
  logfile = '.'.join([os.path.splitext(__file__)[0], 'log'])
  if os.getenv('DEBUG'):
    logging.basicConfig(filename = logfile, filemode = 'w', level = logging.DEBUG)
  else:
    logging.basicConfig(filename = logfile, filemode = 'w', level = logging.INFO)

  audio_files_to_process = get_audio_fileset(sys.argv[1:])
  for audio_file_to_process in audio_files_to_process:
    input_audiofile = AudioFile(audio_file_to_process)
    opus_filename = get_opus_filename(input_audiofile, audio_file_to_process)

    convert_to_opus(audio_file_to_process, opus_filename)

    output_audiofile = AudioFile(opus_filename)
    # update_album_art(input_audiofile, output_audiofile)

    add_replaygain_tags(opus_filename)

    remove_input_file(audio_file_to_process, opus_filename)
