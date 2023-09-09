#!/usr/bin/env python3

import os
import sys
import re
import base64
import logging
import subprocess

import ffmpeg
import mutagen

from pathlib import Path
from pprint import pprint

import wiard

from airtabledata import AirtableData
from audiofile import AudioFile
from memento import MementoData
from tagit_azlyrics import TagitAzlyrics
from tagit_spotify import TagitSpotify


#
# 1. [done] get artist and title from filename and parent directory
# 2. [done] get data from airtable
# 3. [done] get data from spotify
# 4. [done] get lyrics from azlyrics
# 5. [done] convert file to opus, if needed
# 6. [done] delete any existing metadata from opus file
# 7. [done] add metadata to opus file
# 8. [done] add replaygain tags to opus file
# 9. [done] rename file, if needed
#


def convert_file_type(input_audiofile, output_filename):
  logging.debug('Converting "' + input_audiofile.filename +  '" to "' + output_filename + '"')
  ffmpeg                                                  \
    .input(input_audiofile.filename)                      \
    .output(output_filename, **{'acodec':  'libopus'})    \
    .overwrite_output()                                   \
    .run()


def get_album_art(output_audiofile, spotify_data):
  album_art_filename = None

  local_filename = spotify_data._album_art_filename
  if '/' in local_filename:
    local_filename = re.sub('/', '-', local_filename)

  if Path(local_filename).exists():
    album_art_filename = local_filename
  elif spotify_data._album_art_filename:
    album_art_filename = spotify_data._album_art_filename

  if not Path(album_art_filename).exists():
    print('Local album art file not found')
    return None

  if output_audiofile._type == AudioFile._TYPE_MP3:
    with open(album_art_filename, 'rb') as albumart:
      output_audiofile._newTags.album_art = mutagen.id3.APIC(
        encoding = 3,
        mime = AudioFile._MIME_IMAGE_JPEG,
        type = mutagen.id3.PictureType.COVER_FRONT,
        desc = u'Cover',
        data = albumart.read()
      )
  else:
    with open(album_art_filename, 'rb') as albumart:
      picture = mutagen.flac.Picture()
      picture.data = albumart.read()
      picture.type = mutagen.id3.PictureType.COVER_FRONT
      picture.mime = AudioFile._MIME_IMAGE_JPEG
      encoded_data = base64.b64encode(picture.write())
      output_audiofile._newTags.album_art = encoded_data.decode('ascii')

  
def get_artist(file_artist):
  default = file_artist
  if ', The' in default:
    default = 'The ' + default.replace(', The', '')

  return get_input(AudioFile._LABEL_ARTIST.title(), default)


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


def get_input(prompt_text, default = None):
  label = prompt_text
  if default:
    label = label + ' [' + str(default) + ']'
  label = label + ': '

  value = input(label)
  if not value:
    return default

  return value


def get_output_filename(input_audiofile):
  if input_audiofile.type == AudioFile._TYPE_MP3:
    return input_audiofile.filename.replace(AudioFile._EXT_MP3, AudioFile._EXT_OGG_OPUS)
  elif input_audiofile.type == AudioFile._TYPE_OGG_VORBIS:
    return input_audiofile.filename.replace(AudioFile._EXT_OGG_VORBIS, AudioFile._EXT_OGG_OPUS)
  elif input_audiofile.type == AudioFile._TYPE_OGG_OPUS:
    return input_audiofile.filename


def get_title(file_title):
  default = file_title
  return get_input(AudioFile._LABEL_ARTIST.title(), default)


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


def remove_input_file(input_audiofile, output_audiofile):
  if input_audiofile.filename != output_audiofile.filename:
    if Path(input_audiofile.filename).exists() and Path(output_audiofile.filename).exists():
      print('Removing: ' + input_audiofile.filename)
      Path(input_audiofile.filename).unlink()


def set_output_audiofile_tags(output_audiofile, artist, title, spotify_data, airtable_data, azlyrics_data):
  output_audiofile._newTags.artist = artist        
  output_audiofile._newTags.title = title
  
  print(spotify_data)

  if spotify_data.album:
    output_audiofile._newTags.album = spotify_data.album
  else:
    output_audiofile._newTags.album = get_input(AudioFile._LABEL_ALBUM.title())

  if spotify_data.albumartist:
    output_audiofile._newTags.albumartist = spotify_data.albumartist
  else:
    output_audiofile._newTags.albumartist = artist

  if airtable_data.genre:
    output_audiofile._newTags.genre = airtable_data.genre
  else:
    output_audiofile._newTags.genre = get_input(AudioFile._LABEL_GENRE.title())

  if spotify_data.date:
    output_audiofile._newTags.date = spotify_data.date
  else:
    output_audiofile._newTags.date = get_input(AudioFile._LABEL_GENRE.title())

  if azlyrics_data.lyrics:
    output_audiofile._newTags.lyrics = azlyrics_data.lyrics

  get_album_art(output_audiofile, spotify_data)



def update_metadata(output_audiofile):
  output_audiofile._mf.delete()
  output_audiofile._mf.save()

  #print(output_audiofile._newTags.albumartist)

  output_audiofile._mf[AudioFile._LABEL_TITLE] = output_audiofile._newTags.title
  output_audiofile._mf[AudioFile._LABEL_ALBUM] = output_audiofile._newTags.album
  output_audiofile._mf[AudioFile._LABEL_ARTIST] = output_audiofile._newTags.artist
  output_audiofile._mf[AudioFile._LABEL_ALBUMARTIST] = output_audiofile._newTags.albumartist
  output_audiofile._mf[AudioFile._LABEL_DATE] = output_audiofile._newTags.date
  output_audiofile._mf[AudioFile._LABEL_GENRE] = output_audiofile._newTags.genre
  if output_audiofile._newTags.comment:
    output_audiofile._mf[AudioFile._LABEL_COMMENT] = output_audiofile._newTags.comment
  if output_audiofile._newTags.lyrics:
    output_audiofile._mf[AudioFile._LABEL_LYRICS] = output_audiofile._newTags.lyrics
  if output_audiofile._newTags.album_art:
    output_audiofile._mf['METADATA_BLOCK_PICTURE'] = output_audiofile._newTags.album_art

  output_audiofile._mf.save()


def update_replaygain(output_audiofile):
  print('Applying ReplayGain tags...')
  process = subprocess.run(['r128gain', '-v', 'warning', output_audiofile.filename], capture_output=True, text=True)
  if process.returncode != 0:
    print('Failed to upsert replaygain tags')
    print('----')
    print(process.stdout)
    print('----')
    print(process.stderr)
    print('----')


if __name__  == '__main__':
  wiard.get_log_file(__file__)

  audio_files_to_process = get_audio_fileset(sys.argv[1:])

  for input_audiofile in audio_files_to_process:
    logging.debug('Audio file to process: %s' % input_audiofile.filename)

    file_title = Path(input_audiofile.filename).stem
    file_artist = Path(input_audiofile.filename).parent.stem

    artist = get_artist(file_artist)
    title = get_title(file_title)

    memento_data = MementoData(artist, title)
    exit()
    #airtable_data = AirtableData(artist, title)

    spotify_data = TagitSpotify(artist, title)
    spotify_data._get_metadata()

    azlyrics_data = TagitAzlyrics(artist, title)
    azlyrics_data.get_lyrics()

    output_filename = get_output_filename(input_audiofile)
    if input_audiofile.filename != output_filename:
      convert_file_type(input_audiofile, output_filename)
      output_audiofile = AudioFile(output_filename)
    else:
      output_audiofile = input_audiofile


    set_output_audiofile_tags(output_audiofile, artist, title, spotify_data, airtable_data, azlyrics_data)

    update_metadata(output_audiofile)
    
    update_replaygain(output_audiofile)

    remove_input_file(input_audiofile, output_audiofile)

    Path('.cache').unlink()
