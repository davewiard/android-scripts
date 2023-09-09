#!/usr/bin/env python3

import json
import urllib.parse

import urllib.request as urllib2

import tagit_config
import wiard


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
  def library(self):
    return self._library


  @property
  def title(self):
    return ''


  def __init__(self, artist, title):
    self._library = 'Music'

    library_id = get_memento_cloud_library_id(tagit_config._MEMENTO_DATABASE_LIBRARY_NAME)
    entry_ids = get_memento_cloud_library_entry_ids(library_id)
    print(entry_ids)
    entry = get_memento_cloud_library_entry(library_id, entry_ids, artist_name, title)
    print('----')
    print(entry)
    genres = get_entry_genres(entry)
    print(genres)








  def get_entry_field(entry, field_name):
    for field in entry['fields']:
      if field['name'] == field_name:
        return field['value']


  def get_entry_genres(entry):
    return get_entry_field(entry, self._FIELD_GENRE)
    #return entry['fields'][3]['value']


  def get_memento_cloud_library_entry(library_id, entry_ids, artist_name, title):
    if library_id == None:
      return None

    if len(entry_ids) > 8:
      print('Not sure how to do this yet, would generate too many requests')
      return None

    for entry_id in entry_ids:
      url = 'https://api.mementodatabase.com/v1/libraries/' + library_id + '/entries/' + entry_id +  '?'
      params = { 'token': tagit_config._MEMENTO_DATABASE_API_TOKEN }
      full_url = url + urllib.parse.urlencode(params)

      print(full_url)
    
      request = urllib2.Request(full_url)
      response_body = urllib2.urlopen(request).read()
      print(response_body)
      print('')

      response_json = json.loads(response_body)
      fields = response_json['fields']
      if fields[1]['value'] == artist_name and fields[2]['value'] == title:
        return response_json


  def get_memento_cloud_library_entry_ids(library_id):
    if library_id == None:
      return None

    url = 'https://api.mementodatabase.com/v1/libraries/' + library_id + '/entries?'
    params = { 'token': tagit_config._MEMENTO_DATABASE_API_TOKEN }
    full_url = url + urllib.parse.urlencode(params)

    print(full_url)
  
    request = urllib2.Request(full_url)
    response_body = urllib2.urlopen(request).read()
    print(response_body)
    print('')

    response_json = json.loads(response_body)
    return [ e['id'] for e in response_json['entries'] ]


  def get_memento_cloud_library_id(name):
    if name == None:
      return None

    url = 'https://api.mementodatabase.com/v1/libraries?'
    params = { 'token': tagit_config._MEMENTO_DATABASE_API_TOKEN }
    full_url = url + urllib.parse.urlencode(params)
  
    print(full_url)

    request = urllib2.Request(full_url)
    response_body = urllib2.urlopen(request).read()
    print(response_body)
    print('')

    response_json = json.loads(response_body)
    for library in response_json['libraries']:
      if library['name'] == tagit_config._MEMENTO_DATABASE_LIBRARY_NAME:
        return library['id']


if __name__ == '__main__':
  artist_name = 'Dua Lipa'
  title = 'Levitating'

  library_id = get_memento_cloud_library_id(tagit_config._MEMENTO_DATABASE_LIBRARY_NAME)
  entry_ids = get_memento_cloud_library_entry_ids(library_id)
  print(entry_ids)
  entry = get_memento_cloud_library_entry(library_id, entry_ids, artist_name, title)
  print('----')
  print(entry)
  genres = get_entry_genres(entry)
  print(genres)
