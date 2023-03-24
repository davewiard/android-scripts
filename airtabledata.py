from airtable import airtable
from metadata import Metadata

import tagit_config


class AirtableData(Metadata):

  _FIELD_TITLE = 'Title'
  _FIELD_ARTIST = 'Artist'
  _FIELD_ALBUM = 'Album'
  _FIELD_ALBUM_ART = 'Album Art'
  _FIELD_DATE = 'Date'
  _FIELD_GENRE = 'Genre'
  _FIELD_COMMENT = 'Comment'
  _FIELD_URL = 'url'


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
      return '; '.join(value)


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

    #print(artist)
    #print(title)

    at = airtable.Airtable(tagit_config._AIRTABLE_BASE_ID_MUSIC,
                           tagit_config._AIRTABLE_API_KEY)

    print('Fetching Airtable data...')
    records = at.get(self._table, filter_by_formula='{Artist}="' + artist + '"')
    #print(records)
    for record in records['records']:
      if self._get_field(record, AirtableData._FIELD_ARTIST) == artist and     \
         self._get_field(record, AirtableData._FIELD_TITLE) == title:
        #print(record)
        self._record = record
        break
