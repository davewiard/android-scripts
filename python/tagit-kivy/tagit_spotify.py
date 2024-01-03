#!/usr/bin/env python3

import os
import re
import logging
import requests

from pprint import pprint

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

import tagit_config


class TagitSpotify:
  
  _path = None

  _artist = None
  _album = None
  _albumartist = None
  _album_art_filename = None
  _album_art_uri = None
  _date = None
  _title = None
  
  _album_data = None
  _all_album_data = None
  
  _search_artist = None

  _sp = None
  _sp_metadata = None


  @property
  def album(self):
    return self._album


  @album.setter
  def album(self, value):
      self._album = value


  @property
  def album_data(self):
    return self._album_data


  @property
  def all_album_data(self):
    return self._all_album_data


  @property
  def albumartist(self):
    return self._albumartist


  @albumartist.setter
  def albumartist(self, value):
    self._albumartist = value


  @property
  def album_art_filename(self):
    return self._album_art_filename


  @album_art_filename.setter
  def album_art_filename(self, value):
    self._album_art_filename = value


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


  def __init__(self, artist, title, path):
    client_credentials_manager = SpotifyClientCredentials(client_id=tagit_config._SPOTIFY_CLIENT_ID, client_secret=tagit_config._SPOTIFY_CLIENT_SECRET)
    self._sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

    self._search_artist = artist
    self._title = title
    
    self._path = path
    print(self._path)
    
    self._get_metadata()


  def _get_album_art(self):
    if self._album:
      self._album_art_filename = os.path.join(self._path, re.sub(r'[:/\?]', r'-', self._album) + '.jpg')
      r = requests.get(self._album_art_uri)
      open(self._album_art_filename, 'wb').write(r.content)


  def _get_metadata(self):
    logging.info('Fetching Spotify data...')

    # Spotify search doesn't appear to work correctly with at least some special characters included 
    pattern = r'[\'\*\?]'
    search_artist = re.sub(pattern, '', self._search_artist)
    search_title = re.sub(pattern, '', self._title)

    self._metadata = self._sp.search(q='artist:' + search_artist + ' track:' + search_title,
                                     type='track', market='US')
    pprint(self._metadata)

    self._get_album_data()
    self._get_metadata_artist()
    self._get_metadata_album()
    self._get_metadata_albumartist()
    self._get_metadata_date()
    self._get_metadata_album_art_uri()
    self._get_album_art()


  def _get_album_data(self):
    albums = []
    
    try:
      for item in self._metadata['tracks']['items']:
        print(item['album']['album_type'])
        print(self._title)
        print(item['name'])
        if item['album']['album_type'] == 'album' or item['album']['album_type'] == 'single':
          albums.append(item['album'])

      #if len(albums) == 0:
      #  for item in self._metadata['tracks']['items']:
      #    if item['album']['album_type'] == 'single' and item['name'] == self._title:
      #      albums.append(item['album'])

      print('-----')
      pprint(albums)
      print('-----')
      if len(albums) > 0:
        self._album_data = albums[0]

      self._all_album_data = albums
    except:
      pass


  def _get_metadata_album(self):
    try:
      print(self._album_data['name'])
      self._album = self._album_data['name']
    except:
      pass


  def _get_metadata_artist(self):
    artist = None
    try:
      for a in self._album_data['artists']:
        artist = artist + '; ' + a['name'] if artist else a['name']

      self._artist = artist
    except:
      pass


  def _get_metadata_albumartist(self):
    try:
      self._albumartist = self._search_artist
    except:
      pass


  def _get_metadata_date(self):
    try:
      self._date = self._album_data['release_date'].split('-')[0]
    except:
      pass


  def _get_metadata_album_art_uri(self):
    try:
      self._album_art_uri = self._album_data['images'][0]['url']
    except:
      pass


if __name__ == '__main__':
  artist = 'Falling In Reverse'
  title = 'The Drug In Me Is Reimagined'

  ts = TagitSpotify(artist, title)
  print('artist       : ' + ts.artist)
  print('album        : ' + ts.album)
  print('albumartist  : ' + ts.albumartist)
  print('date         : ' + ts.date)
  print('album_art_uri: ' + ts.album_art_uri)
