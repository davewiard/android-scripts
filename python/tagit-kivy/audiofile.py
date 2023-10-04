import logging
import mutagen

from metadata import Metadata
from tags import Tags


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
    self._mf = None

    self._oldTags = Tags()
    self._newTags = Tags()

    self.filename = filename
    self._mf = mutagen.File(self.filename)
    self._set_file_type()
    self.get_old_tags()


  @property
  def mf(self):
    return self._mf


  @property
  def oldTags(self):
    return self._oldTags


  @property
  def type(self):
    return self._type


  @type.setter
  def type(self, value):
    if value not in [AudioFile._TYPE_FLAC, AudioFile._TYPE_MP3, AudioFile._TYPE_OGG_OPUS, AudioFile._TYPE_OGG_VORBIS]:
      raise ValueError('file type "' + value + '" not supported')

    self._type = value


  def _set_file_type(self):
    mft = self._mf.info.pprint().split(',')[0]
    logging.debug('detected file type = ' + mft)
    if mft == 'FLAC':
      self._type = AudioFile._TYPE_FLAC
    elif mft == 'MPEG 1 layer 3':
      self._type = AudioFile._TYPE_MP3
    elif mft == 'Ogg Opus':
      self._type = AudioFile._TYPE_OGG_OPUS
    elif mft == 'Ogg Vorbis':
      self._type = AudioFile._TYPE_OGG_VORBIS


  def get_old_tags(self):
    if self._type == AudioFile._TYPE_MP3:
      self._oldTags.title = self.get_mp3_tag(AudioFile._LABELS_MP3[AudioFile._LABEL_TITLE])
      self._oldTags.artist = self.get_mp3_tag(AudioFile._LABELS_MP3[AudioFile._LABEL_ARTIST])
      self._oldTags.album = self.get_mp3_tag(AudioFile._LABELS_MP3[AudioFile._LABEL_ALBUM])
      self._oldTags.albumartist = self.get_mp3_tag(AudioFile._LABELS_MP3[AudioFile._LABEL_ALBUMARTIST])
      self._oldTags.date = self.get_mp3_tag(AudioFile._LABELS_MP3[AudioFile._LABEL_DATE])
      self._oldTags.genre = self.get_mp3_tag(AudioFile._LABELS_MP3[AudioFile._LABEL_GENRE])
      self._oldTags.comment = self.get_mp3_tag(AudioFile._LABELS_MP3[AudioFile._LABEL_COMMENT])
      self._oldTags.lyrics = self.get_mp3_tag(AudioFile._LABELS_MP3[AudioFile._LABEL_LYRICS])
    else:
      self._oldTags.title = self.get_vorbis_tag(AudioFile._LABEL_TITLE)
      self._oldTags.artist = self.get_vorbis_tag(AudioFile._LABEL_ARTIST)
      self._oldTags.album = self.get_vorbis_tag(AudioFile._LABEL_ALBUM)
      self._oldTags.albumartist = self.get_vorbis_tag(AudioFile._LABEL_ALBUMARTIST)
      self._oldTags.date = self.get_vorbis_tag(AudioFile._LABEL_DATE)
      self._oldTags.genre = self.get_vorbis_tag(AudioFile._LABEL_GENRE)
      self._oldTags.comment = self.get_vorbis_tag(AudioFile._LABEL_COMMENT)
      self._oldTags.lyrics = self.get_vorbis_tag(AudioFile._LABEL_LYRICS)

    if self._type == AudioFile._TYPE_MP3:
      self._oldTags.album_art = self.mf.tags.getall('APIC')
    else:
      for value in self._mf.tags.get('METADATA_BLOCK_PICTURE', []):
        self._oldTags.album_art.append(value)


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
      return self._mf.tags.get(name)
    except KeyError:
      return None    


