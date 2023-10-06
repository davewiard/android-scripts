#!/usr/bin/env python3

import logging
import re

from azlyrics.azlyrics import lyrics


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
    # sanitize title for azlyrics, can't have special characters or azlyrics chokes
    self._title = re.sub('[!:?\'()\[\]]', '', value)


  def __init__(self, artist, title):
    self._artist = artist
    self.title = title


  def get_lyrics(self):
    print('Fetching lyrics for "' + self._title + '" by "' + self._artist + '" ...')
    try:
      azl = lyrics(self._artist, self._title)
      self._lyrics = ''.join(azl).strip()
      print(self._lyrics)
    except Exception as err:
      print(f"Unexpected {err=}, {type(err)=}")
      raise


if __name__ == '__main__':
  pass
