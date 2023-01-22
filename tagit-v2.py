#!/usr/bin/env python3

import os
import sys
import re
import base64
import logging
import subprocess
import requests

import mutagen
import ffmpeg
import azlyrics
from airtabledata import AirtableData

from audiofile import AudioFile
from metadata import Metadata
from pathlib import Path
from tags import Tags

import tagit_config


__version__ = '2.0.0'


#
# 1. [done] get list of input files to process
# 2. [done] get input file details
# 3. [done] convert file to opus
#    a. remove input file after opus successfully created
# 4. [done] get new tags
# 5. [done] update metadata tags
# 6. [done] rename file
# 7. [done] apply replaygain
#

def convert_to_opus(input_filename, output_filename):
  if AudioFile._EXT_OGG_OPUS not in input_filename:
    logging.debug('converting "' + input_filename +  '" to "' + output_filename + '"')
    ffmpeg                                                  \
      .input(input_filename)                                \
      .output(output_filename, **{'acodec':  'libopus'})    \
      .overwrite_output()                                   \
      .run()


def get_airtable_data(output_audiofile):
  output_audiofile._atd = AirtableData(output_audiofile._newTags.artist, output_audiofile._newTags.title)


def get_audio_fileset(fileset):
  result = []

  if len(fileset) > 0:
    return fileset

  for (dir, _, files) in os.walk(os.getcwd()):
    for f in files:
      if is_matching_file_type(os.path.join(dir, f), [AudioFile._TYPE_MP3, AudioFile._TYPE_OGG_OPUS, AudioFile._TYPE_OGG_VORBIS]):
        result.append(os.path.join(dir, f))

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


def get_new_tag_title(output_audiofile):
  default = None

  if output_audiofile._oldTags.title:
    default = output_audiofile._oldTags.title
  else:
    default = Path(output_audiofile.filename).stem

  output_audiofile._newTags.title = get_input(AudioFile._LABEL_TITLE.title(), default)


def get_new_tag_artist(output_audiofile):
  default = None

  artist_dir_name = os.getcwd().split(os.sep)[-1]

  if artist_dir_name == output_audiofile._oldTags.artist:
    default = output_audiofile._oldTags.artist
  else:
    default = artist_dir_name
    if ', The' in default:
      default = 'The ' + default.replace(', The', '')

  output_audiofile._newTags.artist = get_input(AudioFile._LABEL_ARTIST.title(), default)


def get_new_tag_albumartist(output_audiofile):
  default = output_audiofile._newTags.artist
  output_audiofile._newTags.albumartist = get_input(AudioFile._LABEL_ALBUMARTIST.title(), default)


def get_new_tag_album(output_audiofile):
  default = None
  
  #print('here')
  #print(output_audiofile._atd)

  if output_audiofile._atd:
    default = output_audiofile._atd.album
  else:
    image_fileset = glob.glob('*.jpg')
    if len(image_fileset) == 1:
      default = Path(image_fileset[0]).stem
    else:
      default = output_audiofile._oldTags.album

  output_audiofile._newTags.album = get_input(AudioFile._LABEL_ALBUM.title(), default)


def get_new_tag_date(output_audiofile):
  default = None

  if output_audiofile._atd and output_audiofile._atd.date:
    default = output_audiofile._atd.date
  else:
    default = output_audiofile._oldTags.date

  output_audiofile._newTags.date = get_input(AudioFile._LABEL_DATE.title(), default)


def get_new_tag_genre(output_audiofile):
  default = None

  if output_audiofile._atd and output_audiofile._atd.genre:
    default = output_audiofile._atd.genre
  else:
    default = output_audiofile._oldTags.genre

  output_audiofile._newTags.genre = get_input(AudioFile._LABEL_GENRE.title(), default)


def get_new_tag_comment(output_audiofile):
  default = None

  if output_audiofile._atd and output_audiofile._atd.comment:
    default = output_audiofile._atd.comment
  else:
    default = output_audiofile._oldTags.comment

  output_audiofile._newTags.comment = get_input(AudioFile._LABEL_COMMENT.title(), default)


def get_new_tag_lyrics(output_audiofile):
  artist = None
  if ';' in output_audiofile._newTags.artist:
    artist = output_audiofile._newTags.albumartist
  else:
    artist = re.sub('^The ', '', output_audiofile._newTags.artist)

  if "in' " in output_audiofile._newTags.title:
    title = re.sub("in' ", 'ing ', output_audiofile._newTags.title)
  else:
    title = output_audiofile._newTags.title

  if output_audiofile._oldTags and output_audiofile._oldTags.lyrics:
    output_audiofile._newTags.lyrics = output_audiofile._oldTags.lyrics
  else:
    print('Fetching lyrics for "' + title + '" by "' + artist + '" ...')
    lyrics = None
    try:
      az = azlyrics.Azlyrics(artist, title)
      print('URI: ' + az.url())
      if az:
        raw_lyrics = az.get_lyrics()
        formatted_lyrics = az.format_lyrics(raw_lyrics).lstrip().rstrip()

      output_audiofile._newTags.lyrics = formatted_lyrics
    except:
      print('Lyrics not found')


def get_new_album_art(output_audiofile):
  album_art_filename = None

  local_filename = output_audiofile._newTags.album + AudioFile._EXT_JPG
  if '/' in local_filename:
    local_filename = re.sub('/', '-', local_filename)
  #print('local_filename = ' + local_filename)
  #print(AudioFile._LABEL_ALBUM_ART.title())
  #print(self._atd.album_art_url)
  if Path(local_filename).exists():
    album_art_filename = local_filename
  elif output_audiofile._atd and output_audiofile._atd.album_art_url:
    #print('getting url from airtable')
    album_art_url = output_audiofile._atd.album_art_url

    print('Downloading album art from Airtable...')

    r = requests.get(album_art_url)
    open(local_filename, 'wb').write(r.content)

    album_art_filename = local_filename

  if not Path(album_art_filename).exists():
    print('Album art file not found')
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
  

def get_new_tags(output_audiofile):
  get_new_tag_title(output_audiofile)
  get_new_tag_artist(output_audiofile)
  get_new_tag_albumartist(output_audiofile)

  get_airtable_data(output_audiofile)

  get_new_tag_album(output_audiofile)
  get_new_tag_date(output_audiofile)
  get_new_tag_genre(output_audiofile)
  get_new_tag_comment(output_audiofile)
  get_new_tag_lyrics(output_audiofile)
  get_new_album_art(output_audiofile)


def get_opus_filename(input_audiofile, filename):
  if input_audiofile.type == AudioFile._TYPE_MP3:
    return filename.replace(AudioFile._EXT_MP3, AudioFile._EXT_OGG_OPUS)
  elif input_audiofile.type == AudioFile._TYPE_OGG_VORBIS:
    return filename.replace(AudioFile._EXT_OGG_VORBIS, AudioFile._EXT_OGG_OPUS)
  elif input_audiofile.type == AudioFile._TYPE_OGG_OPUS:
    return filename


def is_matching_file_type(filename, codecs):
  stream = ffmpeg.probe(filename)['streams'][0]
  codec = stream['codec_name']
  if codec in codecs:
    return True
  else:
    return False


def remove_file(input_audiofile, output_audiofile):
  if input_audiofile.filename != output_audiofile.filename:
    if Path(input_audiofile.filename).exists() and Path(output_audiofile.filename).exists():
      print('Removing: ' + input_audiofile.filename)
      Path(input_audiofile.filename).unlink()


def rename_file(input_audiofile, output_audiofile):
  # do nothing if mp3 and opus files both exist
  if Path(input_audiofile.filename).exists() and Path(output_audiofile.filename).exists():
    return None

  existing = Path(input_audiofile.filename)

  if input_audiofile.filename != output_audiofile.filename:
    print('Renaming from: ' + input_audiofile.filename)
    print('           to: ' + output_audiofile.filename)
    existing.rename(Path(existing.parent, output_audiofile.filename))


def update_metadata(output_audiofile):
  if output_audiofile._type == AudioFile._TYPE_MP3:
    update_mp3_metadata(output_audiofile)
  else:
    update_vorbis_metadata(output_audiofile)


def update_mp3_metadata(output_audiofile):
  output_audiofile._mf.delete()
  output_audiofile._mf.save()

  output_audiofile._mf.tags.add(mutagen.id3.TIT2(encoding=3, text=output_audiofile._newTags.title))
  output_audiofile._mf.tags.add(mutagen.id3.TALB(encoding=3, text=output_audiofile._newTags.album))
  output_audiofile._mf.tags.add(mutagen.id3.TPE1(encodimg=1, text=output_audiofile._newTags.artist))
  output_audiofile._mf.tags.add(mutagen.id3.TPE2(encodimg=1, text=output_audiofile._newTags.albumartist))
  output_audiofile._mf.tags.add(mutagen.id3.TDRC(encoding=0, text=output_audiofile._newTags.date))  
  output_audiofile._mf.tags.add(mutagen.id3.TCON(encoding=0, text=output_audiofile._newTags.genre))
  if output_audiofile._newTags.comment:
    output_audiofile._mf.tags.add(mutagen.id3.COMM(encoding=1, lang='XXX', desc='', text=output_audiofile._newTags.comment))
  if output_audiofile._newTags.lyrics:
    output_audiofile._mf.tags.add(mutagen.id3.TXXX(encoding=1, desc=AudioFile._LABEL_LYRICS, text=output_audiofile._newTags.lyrics))
  if output_audiofile._newTags.album_art:
    output_audiofile._mf.tags.add(output_audiofile._newTags.album_art)

  output_audiofile._mf.save()


def update_vorbis_metadata(output_audiofile):
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


if __name__ == '__main__':
  logfile = '.'.join([os.path.splitext(__file__)[0], 'log'])
  if os.getenv('DEBUG'):
    logging.basicConfig(filename = logfile, filemode = 'w', level = logging.DEBUG)
  else:
    logging.basicConfig(filename = logfile, filemode = 'w', level = logging.INFO)

  audio_files_to_process = get_audio_fileset(sys.argv[1:])
  for audio_file_to_process in audio_files_to_process:
    logging.debug('audio file to process: %s' % audio_file_to_process)
    input_audiofile = AudioFile(audio_file_to_process)

    opus_filename = get_opus_filename(input_audiofile, audio_file_to_process)
    logging.debug('opus filename:  %s' %  opus_filename)

    convert_to_opus(audio_file_to_process, opus_filename)

    output_audiofile = AudioFile(opus_filename)

    get_new_tags(output_audiofile)
    update_metadata(output_audiofile)
    rename_file(input_audiofile, output_audiofile)
    update_replaygain(output_audiofile)
    remove_file(input_audiofile, output_audiofile)
