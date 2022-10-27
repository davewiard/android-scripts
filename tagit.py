#!/usr/bin/env python3

import os
import sys
import logging
import base64
import ffmpeg
import mutagen
import subprocess
import glob
import azlyrics
from airtable import airtable
from pathlib import Path

import tagit_config


class AudioFile:
  _TYPE_MP3 = 'mp3'
  _TYPE_OGG_OPUS = 'opus'
  _TYPE_OGG_VORBIS = 'vorbis'

  _EXT_JPG = '.jpg'
  _EXT_MP3 = '.mp3'
  _EXT_OGG_OPUS = '.opus'
  _EXT_OGG_VORBIS = '.ogg'
  
  _MIME_IMAGE_JPEG = 'image/jpeg'
  
  _LABEL_TITLE = 'TITLE'
  _LABEL_ALBUM = 'ALBUM'
  _LABEL_ARTIST = 'ARTIST'
  _LABEL_ALBUMARTIST = 'ALBUMARTIST'
  _LABEL_DATE = 'DATE'
  _LABEL_GENRE = 'GENRE'
  _LABEL_COMMENT = 'COMMENT'
  _LABEL_LYRICS = 'LYRICS'
  _LABEL_ALBUM_ART = 'ALBUM_ART'
  
  _LABELS_MP3 = {
    _LABEL_TITLE: 'TIT2',
    _LABEL_ALBUM: 'TALB',
    _LABEL_ARTIST: 'TPE1',
    _LABEL_ALBUMARTIST: 'TPE2',
    _LABEL_DATE: 'TDRC',
    _LABEL_GENRE: 'TCON',
    _LABEL_COMMENT: 'COMM',
    _LABEL_LYRICS: 'TXXX:LYRICS'
  }


  def __init__(self, filename):
    self._type = None
    self._old_tags = {}
    self._new_tags = {}
    self._airtable_record = None

    self.filename = filename
    self.mf = mutagen.File(self.filename)
    self._set_file_type()
    self.get_old_tags()


  @property
  def type(self):
    return self._type


  @type.setter
  def type(self, value):
    print(value)
    if value not in [AudioFile._TYPE_MP3, AudioFile._TYPE_OGG_OPUS, AudioFile._TYPE_OGG_VORBIS]:
      raise ValueError('file type "' + value + '" not supported')

    self._type = value


  @property
  def old_tags(self):
    return self._old_tags


  @old_tags.setter
  def old_tags(self, tags):
    self._old_tags = tags
    

  @property
  def new_tags(self):
    return self._new_tags


  @new_tags.setter
  def new_tags(self, tags):
    self._new_tags = tags
    

  def _set_file_type(self):
    mft = self.mf.info.pprint().split(',')[0]
    logging.debug('detected file type = ' + mft)
    if mft == 'MPEG 1 layer 3':
      self._type = AudioFile._TYPE_MP3
    elif mft == 'Ogg Opus':
      self._type = AudioFile._TYPE_OGG_OPUS
    elif mft == 'Ogg Vorbis':
      self._type = AudioFile._TYPE_OGG_VORBIS


  def _get_input(self, prompt_text, default = None):
    label = prompt_text
    if default:
      label = label + ' [' + str(default) + ']'
    label = label + ': '

    value = input(label)
    if not value:
      return default

    return value


  def _get_new_tags_title(self):
    default = None

    if self._old_tags[AudioFile._LABEL_TITLE]:
      default = self._old_tags[AudioFile._LABEL_TITLE].title()
    else:
      default = Path(self.filename).stem
    
    self._new_tags[AudioFile._LABEL_TITLE] = self._get_input(
                                                    AudioFile._LABEL_TITLE.title(),
                                                    default)


  def _get_new_tags_artist(self):
    default = None

    artist_dir_name = os.getcwd().split(os.sep)[-1]

    if artist_dir_name == self._old_tags[AudioFile._LABEL_ARTIST]:
      default = self._old_tags[AudioFile._LABEL_ARTIST]
    else:
      default = artist_dir_name

    self._new_tags[AudioFile._LABEL_ARTIST] = self._get_input(
                                                    AudioFile._LABEL_ARTIST.title(),
                                                    default)


  def _get_new_tags_albumartist(self):
    default = self._new_tags[AudioFile._LABEL_ARTIST]

    self._new_tags[AudioFile._LABEL_ALBUMARTIST] = self._get_input(
                                                      AudioFile._LABEL_ALBUMARTIST.title(),
                                                      default)


  def _get_new_tags_album(self):
    default = None
    
    image_fileset = glob.glob('*.jpg')

    if self._airtable_record and self._airtable_record['fields'].get(AudioFile._LABEL_ALBUM.title()):
      default = self._airtable_record['fields'][AudioFile._LABEL_ALBUM.title()].rstrip()
    elif len(image_fileset) == 1:
      default = Path(image_fileset[0]).stem
    else:
      default = self._old_tags[AudioFile._LABEL_ALBUM]

    self._new_tags[AudioFile._LABEL_ALBUM] = self._get_input(
                        AudioFile._LABEL_ALBUM.title(),
                        default)


  def _get_new_tags_date(self):
    default = None

    if self._airtable_record and self._airtable_record['fields'].get(AudioFile._LABEL_DATE.title()):
      default = self._airtable_record['fields'][AudioFile._LABEL_DATE.title()]
    else:
      default = self._old_tags[AudioFile._LABEL_DATE]
      
    self._new_tags[AudioFile._LABEL_DATE] = self._get_input(
                        AudioFile._LABEL_DATE.title(),
                        default)


  def _get_new_tags_genre(self):
    default = None

    if self._airtable_record and self._airtable_record['fields'].get(AudioFile._LABEL_GENRE.title()):
      default = self._airtable_record['fields'][AudioFile._LABEL_GENRE.title()].rstrip()
    else:
      default = self._old_tags[AudioFile._LABEL_GENRE]

    self._new_tags[AudioFile._LABEL_GENRE] = self._get_input(
                        AudioFile._LABEL_GENRE.title(),
                        default)


  def _get_new_tags_comment(self):
    default = None

    if self._airtable_record and self._airtable_record['fields'].get(AudioFile._LABEL_COMMENT.title()):
      default = self._airtable_record['fields'][AudioFile._LABEL_COMMENT.title()].rstrip()
    else:
      default = self._old_tags[AudioFile._LABEL_COMMENT]

    self._new_tags[AudioFile._LABEL_COMMENT] = self._get_input(
                        AudioFile._LABEL_COMMENT.title(),
                        default)


  def get_new_tags(self):
    
    self._get_new_tags_title()
    self._get_new_tags_artist()
    self._get_new_tags_albumartist()

    self._get_airtable_record()
    
    self._get_new_tags_album()
    self._get_new_tags_date()
    self._get_new_tags_genre()
    self._get_new_tags_comment()

    if self._old_tags[AudioFile._LABEL_LYRICS]:
      self._new_tags[AudioFile._LABEL_LYRICS] = self._old_tags[AudioFile._LABEL_LYRICS]
    else:
      print('Fetching lyrics ...')
      lyrics = None
      az = azlyrics.Azlyrics(self._new_tags[AudioFile._LABEL_ARTIST],
                             self._new_tags[AudioFile._LABEL_TITLE])
      if az:
        raw_lyrics = az.get_lyrics()
        lyrics = az.format_lyrics(raw_lyrics).lstrip().rstrip()

      self._new_tags[AudioFile._LABEL_LYRICS] = lyrics

    self._new_tags[AudioFile._LABEL_ALBUM_ART] = self.get_new_album_art()

    #print(self._new_tags)


  def get_new_album_art(self):
    album_art_filename = self._new_tags[AudioFile._LABEL_ALBUM] + AudioFile._EXT_JPG

    if not Path(album_art_filename).exists():
      return None

    if self._type == AudioFile._TYPE_MP3:
      with open(album_art_filename, 'rb') as albumart:
        return mutagen.id3.APIC(
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
        return encoded_data.decode('ascii')


  def _get_airtable_record(self):
    title = self._new_tags[AudioFile._LABEL_TITLE]
    artist = self._new_tags[AudioFile._LABEL_ARTIST]
    
    at = airtable.Airtable(tagit_config._AIRTABLE_BASE_ID_MUSIC,
                           tagit_config._AIRTABLE_API_KEY)
    
    records = at.get(tagit_config._AIRTABLE_TABLE_TO_DOWNLOAD)
    #print(records)
    for record in records['records']:
      if record['fields'][AudioFile._LABEL_ARTIST.title()] == artist and record['fields'][AudioFile._LABEL_TITLE.title()] == title:
        self._airtable_record = record
        #print(record)
        return


  def get_old_tags(self):
    self._old_tags[AudioFile._LABEL_ALBUM_ART] = []

    for label in [
      AudioFile._LABEL_TITLE,
      AudioFile._LABEL_ALBUM,
      AudioFile._LABEL_ARTIST,
      AudioFile._LABEL_ALBUMARTIST,
      AudioFile._LABEL_DATE,
      AudioFile._LABEL_GENRE,
      AudioFile._LABEL_COMMENT,
      AudioFile._LABEL_LYRICS
    ]:
      if self._type == AudioFile._TYPE_MP3:
        self._old_tags[label] = self.get_mp3_tag(AudioFile._LABELS_MP3[label])
      else:
        self._old_tags[label] = self.get_vorbis_tag(label)

    if self._type == AudioFile._TYPE_MP3:
      self._old_tags[AudioFile._LABEL_ALBUM_ART] = self.mf.tags.getall('APIC')
    else:
      for value in self.mf.tags.get('METADATA_BLOCK_PICTURE', []):
        self._old_tags[AudioFile._LABEL_ALBUM_ART].append(value)


  def get_mp3_tag(self, name):
    try:
      return self.get_tag(name).text[0]
    except AttributeError:
      return None
    except KeyError:
      return None


  def get_vorbis_tag(self, name):
    try:
      tag = self.get_tag(name)
      if tag != None:
        return tag[0]
    except KeyError:
      return None


  def get_tag(self, name):
    try:
      return self.mf.tags.get(name)
    except KeyError:
      return None    


  def update_metadata(self):
    if self._type == AudioFile._TYPE_MP3:
      self._update_mp3_metadata()
    else:
      self._update_vorbis_metadata()


  def _update_mp3_metadata(self):
    self.mf.delete()
    self.mf.save()

    self.mf.tags.add(mutagen.id3.TIT2(encoding=3, text=self._new_tags[AudioFile._LABEL_TITLE]))
    self.mf.tags.add(mutagen.id3.TALB(encoding=3, text=self._new_tags[AudioFile._LABEL_ALBUM]))
    self.mf.tags.add(mutagen.id3.TPE1(encodimg=1, text=self._new_tags[AudioFile._LABEL_ARTIST]))
    self.mf.tags.add(mutagen.id3.TPE2(encodimg=1, text=self._new_tags[AudioFile._LABEL_ALBUMARTIST]))
    self.mf.tags.add(mutagen.id3.TDRC(encoding=0, text=str(self._new_tags[AudioFile._LABEL_DATE])))  
    self.mf.tags.add(mutagen.id3.TCON(encoding=0, text=self._new_tags[AudioFile._LABEL_GENRE]))
    if self._new_tags[AudioFile._LABEL_COMMENT]:
      self.mf.tags.add(mutagen.id3.COMM(encoding=1, lang='XXX', desc='', text=self._new_tags[AudioFile._LABEL_COMMENT]))
    if self._new_tags[AudioFile._LABEL_LYRICS]:
      self.mf.tags.add(mutagen.id3.TXXX(encoding=1, desc=AudioFile._LABEL_LYRICS, text=self._new_tags[AudioFile._LABEL_LYRICS]))
    if self._new_tags[AudioFile._LABEL_ALBUM_ART]:
      self.mf.tags.add(self._new_tags[AudioFile._LABEL_ALBUM_ART])
    
    self.mf.save()


  def _update_vorbis_metadata(self):
    self.mf.delete()
    self.mf.save()

    self.mf[AudioFile._LABEL_TITLE] = self._new_tags[AudioFile._LABEL_TITLE]
    self.mf[AudioFile._LABEL_ALBUM] = self._new_tags[AudioFile._LABEL_ALBUM]
    self.mf[AudioFile._LABEL_ARTIST] = self._new_tags[AudioFile._LABEL_ARTIST]
    self.mf[AudioFile._LABEL_ALBUMARTIST] = self._new_tags[AudioFile._LABEL_ALBUMARTIST]
    self.mf[AudioFile._LABEL_DATE] = self._new_tags[AudioFile._LABEL_DATE]
    self.mf[AudioFile._LABEL_GENRE] = self._new_tags[AudioFile._LABEL_GENRE]
    if self._new_tags[AudioFile._LABEL_COMMENT]:
      self.mf[AudioFile._LABEL_COMMENT] = self._new_tags[AudioFile._LABEL_COMMENT]
    if self._new_tags[AudioFile._LABEL_LYRICS]:
      self.mf[AudioFile._LABEL_LYRICS] = self._new_tags[AudioFile._LABEL_LYRICS]
    if self._new_tags[AudioFile._LABEL_ALBUM_ART]:
      self.mf['METADATA_BLOCK_PICTURE'] = self._new_tags[AudioFile._LABEL_ALBUM_ART]
    
    self.mf.save()


  def update_replaygain(self):
    process = subprocess.run(['r128gain', self.filename])
    if process.returncode != 0:
      print('Failed to upsert replaygain tags')


  def rename_file(self):
    #print(self._type)
    existing = Path(self.filename)
    new_filename = None

    if self._type == AudioFile._TYPE_MP3:
      new_filename = ''.join((self._new_tags[AudioFile._LABEL_TITLE], AudioFile._EXT_MP3))
    elif self._type == AudioFile._TYPE_OGG_OPUS:
      new_filename = ''.join((self._new_tags[AudioFile._LABEL_TITLE], AudioFile._EXT_OGG_OPUS))
    elif self._type == AudioFile._TYPE_OGG_VORBIS:
      new_filename = ''.join((self._new_tags[AudioFile._LABEL_TITLE], AudioFile._EXT_OGG_VORBIS))

    if new_filename:
      if self.filename != new_filename:
        print('Renaming from: ' + self.filename)
        print('           to: ' + new_filename)
        existing.rename(Path(existing.parent, new_filename))
        self.filename = new_filename
      


def get_audio_fileset(fileset):
  result = []
  
  if len(fileset) > 0:
    return fileset

  for (dir, _, files) in os.walk(os.getcwd()):
    for f in files:
      if is_matching_file_type(os.path.join(dir, f), [AudioFile._TYPE_MP3, AudioFile._TYPE_OGG_OPUS, AudioFile._TYPE_OGG_VORBIS]):
        result.append(os.path.join(dir, f))
  
  return result


def is_matching_file_type(filename, codecs):
  stream = ffmpeg.probe(filename)['streams'][0]
  codec = stream['codec_name']
  if codec in codecs:
    return True
  else:
    return False


if __name__ == '__main__':
  logfile = '.'.join([os.path.splitext(__file__)[0], 'log'])
  if os.getenv('DEBUG'):
    logging.basicConfig(filename = logfile, filemode = 'w', level = logging.DEBUG)
  else:
    logging.basicConfig(filename = logfile, filemode = 'w', level = logging.INFO)

  audio_files_to_process = get_audio_fileset(sys.argv[1:])
  for audio_file_to_process in audio_files_to_process:
    audiofile = AudioFile(audio_file_to_process)
    audiofile.get_new_tags()
    audiofile.update_metadata()
    audiofile.rename_file()
    audiofile.update_replaygain()
