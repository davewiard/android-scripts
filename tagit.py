#!/usr/bin/env python3

import os
import sys
import re
import logging
import base64
import ffmpeg
import mutagen
import subprocess
import requests
import glob
import azlyrics
from airtable import airtable
from pathlib import Path

import tagit_config


class Tags():
  def __init__(self):
    self._title = None
    self._artist = None
    self._album = None
    self._albumartist = None
    self._date = None
    self._genre = None
    self._comment = None
    self._lyrics = None
    self._album_art = []

  @property
  def title(self):
    return self._title

  @title.setter
  def title(self, value):
    self._title = value

  @property
  def album(self):
    return self._album

  @album.setter
  def album(self, value):
    self._album = value

  @property
  def albumartist(self):
    return self._albumartist

  @albumartist.setter
  def albumartist(self, value):
    self._albumartist = value

  @property
  def date(self):
    return self._date

  @date.setter
  def date(self, value):
    self._date = value

  @property
  def genre(self):
    return self._genre

  @genre.setter
  def genre(self, value):
    self._genre = value

  @property
  def comment(self):
    return self._comment

  @comment.setter
  def comment(self, value):
    self._comment = value

  @property
  def lyrics(self):
    return self._lyrics

  @lyrics.setter
  def lyrics(self, value):
    self._lyrics = value

  @property
  def album_art(self):
    return self._album_art

  @album_art.setter
  def album_art(self, value):
    self._album_art = value


class Metadata():

  _FIELD_TITLE = 'Title'
  _FIELD_ARTIST = 'Artist'
  _FIELD_ALBUM = 'Album'
  _FIELD_DATE = 'Date'
  _FIELD_GENRE = 'Genre'
  _FIELD_COMMENT = 'Comment'
  _FIELD_ALBUM_ART = 'Album Art'
  _FIELD_URL = 'url'

  _TYPE_MP3 = 'mp3'
  _TYPE_OGG_OPUS = 'opus'
  _TYPE_OGG_VORBIS = 'vorbis'

  _EXT_JPG = '.jpg'
  _EXT_MP3 = '.mp3'
  _EXT_OGG_OPUS = '.opus'
  _EXT_OGG_VORBIS = '.ogg'
  
  _MIME_IMAGE_JPEG = 'image/jpeg'



class AirtableData(Metadata):

  @property
  def table(self):
    return self._table;


  @property
  def record(self):
    return self._record;


  @property
  def title(self):
    return self._get_field(self._record, AirtableData._FIELD_TITLE).rstrip()


  @property
  def artist(self):
    return self._get_field(self._record, AirtableData._FIELD_ARTIST).rstrip()


  @property
  def album(self):
    value = self._get_field(self._record, AirtableData._FIELD_ALBUM)
    if value:
      return value.rstrip()


  @property
  def date(self):
    value = self._get_field(self._record, AirtableData._FIELD_DATE)
    if value:
      return str(value)


  @property
  def genre(self):
    value = self._get_field(self._record, AirtableData._FIELD_GENRE)
    if value:
      return value.rstrip()


  @property
  def comment(self):
    value = self._get_field(self._record, AirtableData._FIELD_COMMENT)
    if value:
      return value.rstrip()


  @property
  def album_art_url(self):
    album_art = self._get_field(self._record, AirtableData._FIELD_ALBUM_ART)
    if album_art:
      return album_art[0][AirtableData._FIELD_URL]


  def _get_field(self, record, field):
    if record and record['fields'].get(field):
      return record['fields'].get(field)


  def __init__(self, artist, title):
    self._table = 'Metadata'
    self._record = None

    at = airtable.Airtable(tagit_config._AIRTABLE_BASE_ID_MUSIC,
                           tagit_config._AIRTABLE_API_KEY)

    print('Fetching Airtable data...')
    records = at.get(self._table)
    #print(records)
    for record in records['records']:
      if self._get_field(record, AirtableData._FIELD_ARTIST) == artist and     \
         self._get_field(record, AirtableData._FIELD_TITLE) == title:
        self._record = record
        #print(record)
        break



class AudioFile(Metadata):
  
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
    self._atd = None

    self.oldTags = Tags()
    self.newTags = Tags()

    self.filename = filename
    self.mf = mutagen.File(self.filename)
    self._set_file_type()
    self.get_old_tags()


  @property
  def type(self):
    return self._type


  @type.setter
  def type(self, value):
    #print(value)
    if value not in [AudioFile._TYPE_MP3, AudioFile._TYPE_OGG_OPUS, AudioFile._TYPE_OGG_VORBIS]:
      raise ValueError('file type "' + value + '" not supported')

    self._type = value


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

    if self.oldTags.title:
      default = self.oldTags.title
    else:
      default = Path(self.filename).stem

    self.newTags.title = self._get_input(AudioFile._LABEL_TITLE.title(), default)


  def _get_new_tags_artist(self):
    default = None

    artist_dir_name = os.getcwd().split(os.sep)[-1]

    if artist_dir_name == self.oldTags.artist:
      default = self.oldTags.artist
    else:
      default = artist_dir_name
      if ', The' in default:
        default = 'The ' + default.replace(', The', '')

    self.newTags.artist = self._get_input(AudioFile._LABEL_ARTIST.title(), default)


  def _get_new_tags_albumartist(self):
    default = self.newTags.artist
    self.newTags.albumartist = self._get_input(AudioFile._LABEL_ALBUMARTIST.title(), default)


  def _get_new_tags_album(self):
    default = None
    
    image_fileset = glob.glob('*.jpg')

    if self._atd:
      default = self._atd.album
    elif len(image_fileset) == 1:
      default = Path(image_fileset[0]).stem
    else:
      default = self.oldTags.album

    self.newTags.album = self._get_input(AudioFile._LABEL_ALBUM.title(), default)


  def _get_new_tags_date(self):
    default = None

    if self._atd and self._atd.date:
      default = self._atd.date
    else:
      default = self.oldTags.date

    self.newTags.date = self._get_input(AudioFile._LABEL_DATE.title(), default)


  def _get_new_tags_genre(self):
    default = None

    if self._atd and self._atd.genre:
      default = self._atd.genre
    else:
      default = self.oldTags.genre

    self.newTags.genre = self._get_input(AudioFile._LABEL_GENRE.title(), default)


  def _get_new_tags_comment(self):
    default = None

    if self._atd and self._atd.comment:
      default = self._atd.comment
    else:
      default = self.oldTags.comment

    self.newTags.comment = self._get_input(AudioFile._LABEL_COMMENT.title(), default)


  def get_new_tags(self):
    
    self._get_new_tags_title()
    self._get_new_tags_artist()
    self._get_new_tags_albumartist()

    self._atd = AirtableData(self.newTags.artist,self.newTags.title)
    #print(self._atd)
    #self._get_airtable_record()
    
    self._get_new_tags_album()
    self._get_new_tags_date()
    self._get_new_tags_genre()
    self._get_new_tags_comment()
    
    artist = None
    if ';' in self.newTags.artist:
      artist = self.newTags.albumartist
    else:
      artist = re.sub('^The ', '', self.newTags.artist)

    if self.oldTags and self.oldTags.lyrics:
      self.newTags.lyrics = self.oldTags.lyrics
    else:
      print('Fetching lyrics for "' + self.newTags.title + '" by "' + artist + '" ...')
      lyrics = None
      #artist = re.sub('^The ', '', self.newTags.artist)
      az = azlyrics.Azlyrics(artist, self.newTags.title)
      if az:
        raw_lyrics = az.get_lyrics()
        formatted_lyrics = az.format_lyrics(raw_lyrics).lstrip().rstrip()

      self.newTags.lyrics = formatted_lyrics

    self.newTags.album_art = self._get_new_album_art()


  def _get_new_album_art(self):
    album_art_filename = None

    local_filename = self.newTags.album + AudioFile._EXT_JPG
    #print('local_filename = ' + local_filename)
    #print(AudioFile._LABEL_ALBUM_ART.title())
    #print(self._atd.album_art_url)
    if Path(local_filename).exists():
      album_art_filename = local_filename
    elif self._atd and self._atd.album_art_url:
      #print('getting url from airtable')
      album_art_url = self._atd.album_art_url
      
      print('Downloading album art from Airtable...')

      r = requests.get(album_art_url)
      open(local_filename, 'wb').write(r.content)
      
      album_art_filename = local_filename

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


  def get_old_tags(self):
    if self._type == AudioFile._TYPE_MP3:
      self.oldTags.title = self.get_mp3_tag(AudioFile._LABELS_MP3[AudioFile._LABEL_TITLE])
      self.oldTags.artist = self.get_mp3_tag(AudioFile._LABEL_ARTIST)
      self.oldTags.album = self.get_mp3_tag(AudioFile._LABEL_ALBUM)
      self.oldTags.albumartist = self.get_mp3_tag(AudioFile._LABEL_ALBUMARTIST)
      self.oldTags.date = self.get_mp3_tag(AudioFile._LABEL_DATE)
      self.oldTags.genre = self.get_mp3_tag(AudioFile._LABEL_GENRE)
      self.oldTags.comment = self.get_mp3_tag(AudioFile._LABEL_COMMENT)
      self.oldTags.lyrics = self.get_mp3_tag(AudioFile._LABEL_LYRICS)
    else:
      self.oldTags.title = self.get_vorbis_tag(AudioFile._LABEL_TITLE)
      self.oldTags.artist = self.get_vorbis_tag(AudioFile._LABEL_ARTIST)
      self.oldTags.album = self.get_vorbis_tag(AudioFile._LABEL_ALBUM)
      self.oldTags.albumartist = self.get_vorbis_tag(AudioFile._LABEL_ALBUMARTIST)
      self.oldTags.date = self.get_vorbis_tag(AudioFile._LABEL_DATE)
      self.oldTags.genre = self.get_vorbis_tag(AudioFile._LABEL_GENRE)
      self.oldTags.comment = self.get_vorbis_tag(AudioFile._LABEL_COMMENT)
      self.oldTags.lyrics = self.get_vorbis_tag(AudioFile._LABEL_LYRICS)

    if self._type == AudioFile._TYPE_MP3:
      self.oldTags.album_art = self.mf.tags.getall('APIC')
    else:
      for value in self.mf.tags.get('METADATA_BLOCK_PICTURE', []):
        self.oldTags.album_art.append(value)


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

    self.mf.tags.add(mutagen.id3.TIT2(encoding=3, text=self.newTags.title))
    self.mf.tags.add(mutagen.id3.TALB(encoding=3, text=self.newTags.album))
    self.mf.tags.add(mutagen.id3.TPE1(encodimg=1, text=self.newTags.artist))
    self.mf.tags.add(mutagen.id3.TPE2(encodimg=1, text=self.newTags.albumartist))
    self.mf.tags.add(mutagen.id3.TDRC(encoding=0, text=self.newTags.date))  
    self.mf.tags.add(mutagen.id3.TCON(encoding=0, text=self.newTags.genre))
    if self.newTags.comment:
      self.mf.tags.add(mutagen.id3.COMM(encoding=1, lang='XXX', desc='', text=self.newTags.comment))
    if self.newTags.lyrics:
      self.mf.tags.add(mutagen.id3.TXXX(encoding=1, desc=AudioFile._LABEL_LYRICS, text=self.newTags.lyrics))
    if self.newTags.album_art:
      self.mf.tags.add(self.newTags.album_art)
    
    self.mf.save()


  def _update_vorbis_metadata(self):
    self.mf.delete()
    self.mf.save()
    
    #print(self.newTags.albumartist)

    self.mf[AudioFile._LABEL_TITLE] = self.newTags.title
    self.mf[AudioFile._LABEL_ALBUM] = self.newTags.album
    self.mf[AudioFile._LABEL_ARTIST] = self.newTags.artist
    self.mf[AudioFile._LABEL_ALBUMARTIST] = self.newTags.albumartist
    self.mf[AudioFile._LABEL_DATE] = self.newTags.date
    self.mf[AudioFile._LABEL_GENRE] = self.newTags.genre
    if self.newTags.comment:
      self.mf[AudioFile._LABEL_COMMENT] = self.newTags.comment
    if self.newTags.lyrics:
      self.mf[AudioFile._LABEL_LYRICS] = self.newTags.lyrics
    if self.newTags.album_art:
      self.mf['METADATA_BLOCK_PICTURE'] = self.newTags.album_art
    
    self.mf.save()


  def update_replaygain(self):
    print('Applying ReplayGain tags...')
    process = subprocess.run(['r128gain', '-v', 'warning', self.filename])
    if process.returncode != 0:
      print('Failed to upsert replaygain tags')


  def rename_file(self):
    #print(self._type)
    existing = Path(self.filename)
    new_filename = None

    if self._type == AudioFile._TYPE_MP3:
      new_filename = ''.join((self.newTags.title, AudioFile._EXT_MP3))
    elif self._type == AudioFile._TYPE_OGG_OPUS:
      new_filename = ''.join((self.newTags.title, AudioFile._EXT_OGG_OPUS))
    elif self._type == AudioFile._TYPE_OGG_VORBIS:
      new_filename = ''.join((self.newTags.title, AudioFile._EXT_OGG_VORBIS))

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
    logging.info('Processing "%s"' % audio_file_to_process)
    audiofile = AudioFile(audio_file_to_process)
    audiofile.get_new_tags()
    audiofile.update_metadata()
    audiofile.rename_file()
    audiofile.update_replaygain()
