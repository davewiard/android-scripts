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
