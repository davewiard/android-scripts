#!/usr/bin/env python3

import os
import sys
import logging
import ffmpeg
import mutagen

# 1. [done] get list of all audio files in CWD
# 2. [done] get list of all image files in CWD
# 3. [done] prompt user to enter all desired tags
#    a. [done] title, artist, album artist, genre, year, comment, lyrics, album art filename, rating?
#    b. [done] try to auto-detect artist from parent directory name
#    c. [done] offer artist name as default album artist
# 4. update metadata tags
# 5. rename file if needing to be renamed

def get_audio_fileset(fileset):
  result = []
  
  if len(fileset) > 0:
    return fileset

  for (dir, _, files) in os.walk(os.getcwd()):
    for f in files:
      if is_matching_file_type(os.path.join(dir, f), ['mp3', 'opus', 'vorbis']):
        result.append(os.path.join(dir, f))
  
  return result


def get_image_fileset():
  result = []
  
  for (dir, _, files) in os.walk(os.getcwd()):
    for f in files:
      if is_matching_file_type(os.path.join(dir, f), ['mjpeg']):
        result.append(os.path.join(dir, f))
  
  return result


def get_album():
  return input('Album: ')


def get_album_artist(artist):
  album_artist = input('Album Artist [' + artist + ']: ')
  if len(album_artist) > 0:
    return album_artist
  
  return artist


def get_artist():
  # get parent directory name (probably contains artist name)
  dir = os.getcwd().split(os.sep)[-1]

  artist = input('Artist [' + dir + ']: ')
  if len(artist) > 0:
    return artist
  
  return dir


def get_comment():
  return input('Comment: ')


def get_genre():
  return input('Genre: ')


def get_lyrics():
  print('Lyrics:')
  lyrics = []
  while True:
    try:
      line = input()
      if len(line) < 1:
        line = '\n'
    except EOFError:
      break
    lyrics.append(line)
    
  return '\n'.join(lyrics)


def get_tags():
  tags = {}
  
  tags['title'] = get_title()
  if len(tags['title']) < 1:
    return

  tags['album'] = get_album()
  tags['artist'] = get_artist()
  tags['album_artist'] = get_album_artist(tags['artist'])
  tags['year'] = get_year()
  tags['genre'] = get_genre()
  tags['comment'] = get_comment()
  tags['lyrics'] = get_lyrics()
  
  return tags


def get_title():
  return input('Title: ')


def get_year():
  return input('Year: ')


def is_matching_file_type(filename, codecs):
  stream = ffmpeg.probe(filename)['streams'][0]
  codec = stream['codec_name']
  if codec in codecs:
    return True
  else:
    return False


def process_one_file(filename):
  print(filename)
  tags = get_tags()
  print(tags)
  update_metadata(filename, tags)
  return None


def update_metadata(filename, tags):
  mf = mutagen.File(filename)
  mft = mf.info.pprint().split(',')[0]
  if mft == 'MPEG 1 layer 3':
    update_mp3_metadata(mf, tags)
  elif mft == 'Ogg Opus':
    update_opus_metadata(mf, tags)
  elif mft == 'Ogg Vorbis':
    update_vorbis_metdata(mf, tags)


def update_mp3_metadata(mf, tags):
  mf.pop('TIT2')
  mf.tags.add(mutagen.id3.TIT2(encoding=3, text=tags['title']))

  mf.pop('TALB')
  mf.tags.add(mutagen.id3.TALB(encoding=3, text=tags['album']))

  mf.pop('TPE1')
  mf.tags.add(mutagen.id3.TPE1(encodimg=1, text=tags['artist']))

  mf.pop('TPE2')
  mf.tags.add(mutagen.id3.TPE2(encodimg=1, text=tags['album_artist']))
  
  mf.pop('TDRC')
  mf.tags.add(mutagen.id3.TDRC(encoding=0, text=tags['year']))

  mf.pop('TCON')
  mf.tags.add(mutagen.id3.TCON(encoding=0, text=tags['genre']))

  mf.pop('COMM:ID3v1 Comment:eng')
  mf.pop('COMM::XXX')
  mf.tags.add(mutagen.id3.COMM(encoding=1, lang='XXX', desc='', text=tags['comment']))

  mf.pop('TXXX:LYRICS')
  mf.tags.add(mutagen.id3.TXXX(encoding=1, desc='LYRICS', text=tags['lyrics']))
  
  mf.save()


if __name__	== '__main__':
  logfile = '.'.join([os.path.splitext(__file__)[0], 'log'])
  if os.getenv('DEBUG'):
    logging.basicConfig(filename=logfile, filemode='w', level=logging.DEBUG)
  else:
    logging.basicConfig(filename=logfile, filemode='w', level=logging.INFO)

  audio_files_to_process = get_audio_fileset(sys.argv[1:])
  for audio_file_to_process in audio_files_to_process:
    result = process_one_file(audio_file_to_process)
    print('result = %s' % str(result))
