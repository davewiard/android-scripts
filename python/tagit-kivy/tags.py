class Tags:
  def __init__(self):
    self._album = None
    self._albumartist = None
    self._album_art = []
    self._artist = None
    self._comment = None
    self._date = None
    self._genre = None
    self._lyrics = None
    self._title = None

  @property
  def album(self):
    return self._album;

  @album.setter
  def album(self, value):
    self._album = value

  @property
  def albumartist(self):
    return self._albumartist;

  @albumartist.setter
  def albumartist(self, value):
    self._albumartist = value

  @property
  def album_art(self):
    return self._album_art;

  @album_art.setter
  def album_art(self, value):
    self._album_art = value

  @property
  def artist(self):
    return self._artist;

  @artist.setter
  def artist(self, value):
    self._artist = value

  @property
  def comment(self):
    return self._comment;

  @comment.setter
  def comment(self, value):
    self._comment = value

  @property
  def date(self):
    return self._date;

  @date.setter
  def date(self, value):
    self._date = value

  @property
  def genre(self):
    return self._genre;

  @genre.setter
  def genre(self, value):
    self._genre = value

  @property
  def lyrics(self):
    return self._lyrics;

  @lyrics.setter
  def lyrics(self, value):
    self._lyrics = value

  @property
  def title(self):
    return self._title;

  @title.setter
  def title(self, value):
    self._title = value
