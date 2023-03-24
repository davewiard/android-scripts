#!/usr/bin/env python3

import logging

import azlyrics


class TagitAzlyrics:

  _artist = None
  _title = None
  _lyrics = None


  @property
  def artist(self):
    return self._artist


  @artist.setter
  def artist(self, value):
    self._artist = value


  @property
  def lyrics(self):
    return self._lyrics


  @lyrics.setter
  def lyrics(self, value):
    self._lyrics = value


  @property
  def title(self):
    return self.title


  @title.setter
  def title(self, value):
    self._title = value


  def __init__(self, artist, title):
    self._artist = artist
    self.title = title


  def get_lyrics(self):
    print('Fetching lyrics for "' + self._title + '" by "' + self._artist + '" ...')
    try:
      az = azlyrics.Azlyrics(self._artist, self._title)
      logging.debug('URI: ' + az.url())
      if az:
        raw_lyrics = az.get_lyrics()
        formatted_lyrics = az.format_lyrics(raw_lyrics).lstrip().rstrip()

      self._lyrics = formatted_lyrics
    except:
      print('Lyrics not found')


if __name__ == '__main__':
  pass
