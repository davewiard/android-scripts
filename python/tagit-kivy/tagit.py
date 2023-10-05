#!/usr/bin/env python3

import os
import base64
import re

import mutagen

from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.properties import ObjectProperty
from kivy.uix.popup import Popup

from audiofile import AudioFile
from solarized import Solarized
from tagit_spotify import TagitSpotify
from tagit_azlyrics import TagitAzlyrics


class LoadDialog(FloatLayout):
  load = ObjectProperty(None)
  cancel = ObjectProperty(None)


class Root(GridLayout):
  _popup = None
  _audiofile = None
  _spotify_data = None
  colors = Solarized()


  def __init__(self, **kwargs):
    super().__init__(**kwargs)


  def clear_tags(self):
    self._audiofile.mf.delete()
    self._audiofile.mf.save()

    self.set_input_text(self.ids.label_artist, self.ids.input_artist, '')
    self.set_input_text(self.ids.label_albumartist, self.ids.input_albumartist, '')
    self.set_input_text(self.ids.label_album, self.ids.input_album, '')
    self.set_input_text(self.ids.label_title, self.ids.input_title, '')
    self.set_input_text(self.ids.label_date, self.ids.input_date, '')
    self.set_input_text(self.ids.label_genre, self.ids.input_genre, '')
    self.set_input_text(self.ids.label_comment, self.ids.input_comment, '')
    self.set_input_text(self.ids.label_lyrics, self.ids.input_lyrics, '')
    self.ids.album_art.source = ''


  def get_lyrics(self):
    azlyrics_data = TagitAzlyrics(self.ids.input_artist.text, self.ids.input_title.text)
    azlyrics_data.get_lyrics()
    self.set_input_text(self.ids.label_lyrics, self.ids.input_lyrics, azlyrics_data.lyrics.strip())


  def set_input_text(self, l, w, value):
    w.text = value
    if l == self.ids.label_comment:
      self.set_color_label_normal(l)
      return
      
    if len(w.text) < 1:
      self.set_color_label_warning(l)
    else:
      self.set_color_label_normal(l)



  def get_spotify_data(self):
    self._spotify_data = TagitSpotify(self.ids.input_artist.text, self.ids.input_title.text)
    if not self._spotify_data or not self._spotify_data.album_data or len(self._spotify_data.album_data) < 1:
      self.set_color_label_warning(self.ids.label_album)
      self.set_color_label_warning(self.ids.label_date)
      self.set_color_label_warning(self.ids.label_album_art)
      return

    self.set_input_text(self.ids.label_artist, self.ids.input_artist, self._spotify_data.artist)
    self.set_input_text(self.ids.label_albumartist, self.ids.input_albumartist, self._spotify_data.albumartist)
    self.set_input_text(self.ids.label_album, self.ids.input_album, self._spotify_data.album)
    self.set_input_text(self.ids.label_title, self.ids.input_title, self._spotify_data.title)
    self.set_input_text(self.ids.label_date, self.ids.input_date, self._spotify_data.date)
    self.set_input_text(self.ids.label_genre, self.ids.input_genre, '')
    self.set_input_text(self.ids.label_comment, self.ids.input_comment, '')
    self.ids.album_art.source = self._spotify_data.album_art_uri
    self.set_color_label_normal(self.ids.label_album_art)


  def set_color_label_normal(self, w):
    self.set_color(w, self.colors.BASE3)


  def set_color_label_warning(self, w):
    self.set_color(w, self.colors.RED)


  def set_color(self, w, c):
    w.color = self.colors.get_color(c, self.colors.DECIMAL)


  def on_change_input(self, w, l):
    if len(w.text) > 0:
      self.set_color_label_normal(l)
    else:
      self.set_color_label_warning(l)


  def save_tags(self):
    self._audiofile.mf[self._audiofile.LABEL_TITLE] = self.ids.input_title.text
    self._audiofile.mf[self._audiofile.LABEL_ALBUM] = self.ids.input_album.text
    self._audiofile.mf[self._audiofile.LABEL_ARTIST] = self.ids.input_artist.text
    self._audiofile.mf[self._audiofile.LABEL_ALBUMARTIST] = self.ids.input_albumartist.text
    self._audiofile.mf[self._audiofile.LABEL_DATE] = self.ids.input_date.text
    self._audiofile.mf[self._audiofile.LABEL_GENRE] = self.ids.input_genre.text
    if self.ids.input_comment.text:
      self._audiofile.mf[self._audiofile.LABEL_COMMENT] = self.ids.input_comment.text
    if self.ids.input_lyrics.text:
      self._audiofile.mf[self._audiofile.LABEL_LYRICS] = self.ids.input_lyrics.text

    with open(self._spotify_data.album_art_filename, 'rb') as albumart:
      picture = mutagen.flac.Picture()
      picture.data = albumart.read()
      picture.type = mutagen.id3.PictureType.COVER_FRONT
      picture.mime = self._audiofile.MIME_IMAGE_JPEG
      encoded_data = base64.b64encode(picture.write())
      album_art = encoded_data.decode('ascii')
    if album_art:
      self._audiofile.mf['METADATA_BLOCK_PICTURE'] = album_art

    self._audiofile.mf.save()


  def dismiss_popup(self):
    self._popup.dismiss()


  def show_load(self):
    content = LoadDialog(load=self.load, cancel=self.dismiss_popup)
    self._popup = Popup(title="Open file", content=content, size_hint=(0.9, 0.9))
    self._popup.open()


  def load(self, path, filename):
    self.ids.label_filename.text = os.path.join(path, filename[0])
    self._audiofile = AudioFile(os.path.join(self.ids.label_filename.text))

    if self._audiofile.oldTags.artist:
      self.ids.input_artist.text = self._audiofile.oldTags.artist
    if self._audiofile.oldTags.albumartist:
      self.ids.input_albumartist.text = self._audiofile.oldTags.albumartist
    if self._audiofile.oldTags.album:
      self.ids.input_album.text = self._audiofile.oldTags.album
    if self._audiofile.oldTags.title:
      self.ids.input_title.text = self._audiofile.oldTags.title
    if self._audiofile.oldTags.date:
      self.ids.input_date.text = self._audiofile.oldTags.date
    if self._audiofile.oldTags.comment:
      self.ids.input_comment.text = self._audiofile.oldTags.comment

    if self._audiofile.oldTags.album_art:
      # TODO read the album_art 'ascii' data and convert to binary data
      # binary_data= f.read() #image opened in binary mode
      # data = io.BytesIO(binary_data)
      # img=CoreImage(data, ext="png").texture
      # new_img= Image()
      # new_img.texture= img
      pass

    if len(self.ids.input_artist.text) < 1:
      self.set_color_label_warning(self.ids.label_artist)

    if len(self.ids.input_albumartist.text) < 1:
      self.set_color_label_warning(self.ids.label_albumartist)

    if len(self.ids.input_album.text) < 1:
      self.set_color_label_warning(self.ids.label_album)

    if len(self.ids.input_title.text) < 1:
      self.set_color_label_warning(self.ids.label_title)

    if len(self.ids.input_date.text) < 1:
      self.set_color_label_warning(self.ids.label_date)

    if len(self.ids.input_genre.text) < 1:
      self.set_color_label_warning(self.ids.label_genre)

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
