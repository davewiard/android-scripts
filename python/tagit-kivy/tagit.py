#!/usr/bin/env python3

import os
from pprint import pprint

from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.properties import ObjectProperty
from kivy.uix.popup import Popup

from audiofile import AudioFile
from tagit_spotify import TagitSpotify
from tagit_azlyrics import TagitAzlyrics


class LoadDialog(FloatLayout):
  load = ObjectProperty(None)
  cancel = ObjectProperty(None)


class Root(GridLayout):
  _popup = None
  _audiofile = None

  COLORS = {
    'warning': [220/255, 50/255, 47/255, 1],
    'light_text':  [253/255, 246/255, 227/255, 1]
  }

  def __init__(self, **kwargs):
    super(Root, self).__init__(**kwargs)

  def get_lyrics(self):
    azlyrics_data = TagitAzlyrics(self.ids.input_artist.text, self.ids.input_title.text)
    azlyrics_data.get_lyrics()
    self.ids.input_lyrics.text = azlyrics_data.lyrics.strip()

  def get_spotify_data(self):
    spotify_data = TagitSpotify(self.ids.input_artist.text, self.ids.input_title.text)
    if 'spotify_data' not in locals() or not spotify_data.album_data or len(spotify_data.album_data) < 1:
      self.ids.label_album.color = self.COLORS['warning']
      self.ids.label_date.color = self.COLORS['warning']
      self.ids.label_album_art.color = self.COLORS['warning']
      return None
  
    self.ids.input_albumartist.text = spotify_data.albumartist
    self.ids.label_albumartist.color = self.COLORS['light_text']

    self.ids.input_album.text = spotify_data.album
    self.ids.label_album.color = self.COLORS['light_text']

    self.ids.input_date.text = spotify_data.date
    self.ids.label_date.color = self.COLORS['light_text']

    self.ids.input_comment.text = ''
    self.ids.label_comment.color = self.COLORS['light_text']

    self.ids.album_art.source = spotify_data.album_art_uri
    self.ids.label_album_art.color = self.COLORS['light_text']

  def on_change_genre(self):
    if len(self.ids.input_genre.text) > 0:
      self.ids.label_genre.color = self.COLORS['light_text']
    else:
      self.ids.label_genre.color = self.COLORS['warning']

  def dismiss_popup(self):
    self._popup.dismiss()

  def show_load(self):
    content = LoadDialog(load=self.load, cancel=self.dismiss_popup)
    self._popup = Popup(title="Open file", content=content, size_hint=(0.9, 0.9))
    self._popup.open()

  def load(self, path, filename):
    self.ids.label_filename.text = os.path.join(path, filename[0])
    self._audiofile = AudioFile(os.path.join(self.ids.label_filename.text))

    self.ids.input_artist.text = self._audiofile._oldTags.artist
    self.ids.input_albumartist.text = self._audiofile._oldTags.albumartist
    self.ids.input_album.text = self._audiofile._oldTags.album
    self.ids.input_title.text = self._audiofile._oldTags.title
    self.ids.input_date.text = self._audiofile._oldTags.date
    self.ids.input_comment.text = self._audiofile._oldTags.comment

    if len(self.ids.input_artist.text) < 1:
      self.ids.label_artist.color = self.COLORS['warning']

    if len(self.ids.input_albumartist.text) < 1:
      self.ids.label_albumartist.color = self.COLORS['warning']

    if len(self.ids.input_title.text) < 1:
      self.ids.label_title.color = self.COLORS['warning']

    if len(self.ids.input_date.text) < 1:
      self.ids.label_date.color = self.COLORS['warning']

    if len(self.ids.input_genre.text) < 1:
      self.ids.label_genre.color = self.COLORS['warning']

    self.ids.button_save.disabled = False
    self.ids.button_spotify.disabled = False
    self.ids.button_lyrics.disabled = False
    self.ids.button_clear_tags.disabled = False

    self.dismiss_popup()

class TagItApp(App):
  def build(self):
    return Root()


if __name__ == '__main__':
  print('Starting ' +  __file__)
  TagItApp().run()
