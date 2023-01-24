#!/usr/bin/env python3

from pprint import pprint

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

import tagit_config


class TagitSpotify:

  _artist = None
  _album = None
  _albumartist = None
  _album_art_uri = None
  _date = None
  _genre = None
  _title = None

  _sp = None
  _sp_metadata = None


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
  def album_art_uri(self):
    return self._album_art_uri


  @album_art_uri.setter
  def album_art_uri(self, value):
    self._album_art_uri = value


  @property
  def artist(self):
    return self._artist


  @artist.setter
  def artist(self, value):
    self._artist = value


  @property
  def title(self):
    return self._title


  @artist.setter
  def artist(self, value):
    self._title = value


  @property
  def date(self):
    return self._date


  @date.setter
  def date(self, value):
    self._date = value


  def __init__(self, artist, title):
    client_credentials_manager = SpotifyClientCredentials(client_id=tagit_config._SPOTIFY_CLIENT_ID, client_secret=tagit_config._SPOTIFY_CLIENT_SECRET)
    self._sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

    self._artist = artist
    self._title = title


  def get_metadata(self):
    self._metadata = self._sp.search(q='artist:' + self._artist + ' track:' + self._title, 
                                     type='track', market='US', limit=1)
    pprint(self._metadata)

    self._get_metadata_album()
    self._get_metadata_albumartist()
    self._get_metadata_date()
    self._get_metadata_album_art_uri()


  def _get_metadata_album(self):
    self._album = self._metadata['tracks']['items'][0]['album']['name']


  def _get_metadata_albumartist(self):
    self._albumartist = self._metadata['tracks']['items'][0]['album']['artists'][0]['name']


  def _get_metadata_date(self):
    self._date = self._metadata['tracks']['items'][0]['album']['release_date'].split('-')[0]


  def _get_metadata_album_art_uri(self):
    self._album_art_uri = self._metadata['tracks']['items'][0]['album']['images'][0]['url']


if __name__ == '__main__':
  artist = 'Pearl Jam'
  title = 'Black'

  ts = TagitSpotify(artist, title)
  ts.get_metadata()
  print('album        : ' +  ts.album)
  print('albumartist  : ' + ts.albumartist)
  print('date         : ' + ts.date)
  print('album_art_uri: ' +  ts.album_art_uri)
