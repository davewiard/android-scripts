from metadata import Metadata

import tagit_config


class MementoData(Metadata):

  _FIELD_TITLE = 'Title'
  _FIELD_ARTIST = 'Artist'
  _FIELD_ALBUM = 'Album'
  _FIELD_ALBUM_ART = 'Album Art'
  _FIELD_DATE = 'Date'
  _FIELD_GENRE = 'Genre'
  _FIELD_COMMENT = 'Comment'
  _FIELD_URL = 'url'


  @property
  def title(self):
    return ''


  def __init__(self, artist, title):
    self._library = 'Music'
    