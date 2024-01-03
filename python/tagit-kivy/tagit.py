#pylint:disable=R0201
#!/usr/bin/env python3

import os
import base64
import re
import requests

import mutagen

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.properties import ObjectProperty
from kivy.uix.popup import Popup
from kivy.metrics import dp

from audiofile import AudioFile
from solarized import Solarized
from tagit_spotify import TagitSpotify
from tagit_azlyrics import TagitAzlyrics


class LoadDialog(FloatLayout):
  load = ObjectProperty(None)
  cancel = ObjectProperty(None)


class SpotifyDataSelectDialog(FloatLayout):
  album_data = ObjectProperty(None)
  cancel = ObjectProperty(None)


class Resizing_GridLayout(GridLayout):
  pass


class ResizingRow_GridLayout(GridLayout):
  pass


class DarkButton(Button):
  pass


class DarkLabel(Label):
  pass


class Root(GridLayout):
  _popup = None
  _audiofile = None
  _selected_album = None
  _spotify_data = None
  colors = Solarized()


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


  def album_selected(self, instance):
    index = 0
    for obj in self.ids:
      print(obj)
      print(self.ids[obj])
      if self.ids[obj] == instance:
        index = re.sub(r'.*(\d+)$', r'\1', obj)
        break
    album = self._spotify_data.all_album_data[int(index)]
    self._selected_album = album

    self.set_input_text(self.ids.label_albumartist, self.ids.input_albumartist, album['artists'][0]['name'])
    self.set_input_text(self.ids.label_album, self.ids.input_album, album['name'])
    self.set_input_text(self.ids.label_date, self.ids.input_date, album['release_date'][:4])
    self.set_input_text(self.ids.label_genre, self.ids.input_genre, '')
    self.set_input_text(self.ids.label_comment, self.ids.input_comment, '')

    self.ids.album_art.source = album['images'][0]['url']
    album_art_filename = os.path.join(os.path.dirname(self.ids.label_filename.text),
                                      re.sub(r'[\*:/\?]', r'-', self.ids.input_album.text) + '.jpg')
    r = requests.get(album['images'][0]['url'])
    open(album_art_filename, 'wb').write(r.content)
    self.set_color_label_normal(self.ids.label_album_art)
 
    self.dismiss_popup()


  def spotify_layout(self, all_album_data):
    layout = BoxLayout(
      pos=self.pos,
      orientation='vertical',
      padding=20,
      spacing=100
    )

    resizing_gridlayout = Resizing_GridLayout()

    btn_index = 0
    for album in all_album_data:
      resizingrow_gridlayout = ResizingRow_GridLayout()
      box_layout = BoxLayout()
      select_btn = DarkButton(
        size_hint_x=None,
        text='Select',
        width=100
      )
      select_btn.bind(on_press=lambda instance: self.album_selected(instance))
      self.ids['select_btn' + str(btn_index)] = select_btn
      btn_index = btn_index + 1

      date = Label(
        bold=False,
        color=[253/255, 246/255, 227/255, 1],  # base3
        font_name='Roboto',
        font_size=45,
        halign='center',
        padding_y=dp(30),
        size_hint_x=None,
        width=300,
        text=album['release_date']
      )
      album_name = Label(
        bold=False,
        color=[253/255, 246/255, 227/255, 1],  # base3
        font_name='Roboto',
        font_size=45,
        halign='center',
        padding_y=dp(30),
        size_hint_x=None,
        width=800,
        text=album['name']
      )
      spacer = Label(
        bold=False,
        color=[253/255, 246/255, 227/255, 1],  # base3
        font_name='Roboto',
        font_size=45,
        halign='center',
        padding_y=dp(30),
        size_hint_x=1,
        text=''
      )
      box_layout.add_widget(select_btn)
      box_layout.add_widget(date)
      box_layout.add_widget(album_name)
      box_layout.add_widget(spacer)
      resizingrow_gridlayout.add_widget(box_layout)
      resizing_gridlayout.add_widget(resizingrow_gridlayout)
  
    dismiss_row = BoxLayout(
      size_hint_y=None,
      height=30
    )
    dismiss_btn = DarkButton(text='Dismiss')
    dismiss_row.add_widget(dismiss_btn)

    layout.add_widget(resizing_gridlayout)
    layout.add_widget(dismiss_row)
    return layout





  def get_spotify_data(self):
    path = os.path.dirname(self.ids.label_filename.text)
    self._spotify_data = TagitSpotify(self.ids.input_artist.text, self.ids.input_title.text, path)
    self._popup = Popup(title="Select data",
                        content=self.spotify_layout(self._spotify_data.all_album_data),
                        size_hint=(0.9, 0.9))
    self._popup.open()


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
    if self.ids.input_title.text != self._audiofile.oldTags.title:
      self._audiofile.mf[self._audiofile.LABEL_TITLE] = self.ids.input_title.text
    if self.ids.input_album.text != self._audiofile.oldTags.album:
      self._audiofile.mf[self._audiofile.LABEL_ALBUM] = self.ids.input_album.text
    if self.ids.input_artist.text != self._audiofile.oldTags.artist:
      self._audiofile.mf[self._audiofile.LABEL_ARTIST] = self.ids.input_artist.text
    if self.ids.input_albumartist.text != self._audiofile.oldTags.albumartist:
      self._audiofile.mf[self._audiofile.LABEL_ALBUMARTIST] = self.ids.input_albumartist.text
    if self.ids.input_date.text != self._audiofile.oldTags.date:
      self._audiofile.mf[self._audiofile.LABEL_DATE] = self.ids.input_date.text
    if self.ids.input_genre.text != self._audiofile.oldTags.genre:
      self._audiofile.mf[self._audiofile.LABEL_GENRE] = self.ids.input_genre.text
    if self.ids.input_comment.text and self.ids.input_comment.text != self._audiofile.oldTags.comment:
      self._audiofile.mf[self._audiofile.LABEL_COMMENT] = self.ids.input_comment.text
    if self.ids.input_lyrics.text and self.ids.input_lyrics.text != self._audiofile.oldTags.lyrics:
      self._audiofile.mf[self._audiofile.LABEL_LYRICS] = self.ids.input_lyrics.text

    #
    # if the tag already exists leave it as-is
    # if local file was created by retrieving spotify data, apply image to tags
    #
    if self._spotify_data.album_art_filename:
      print("Trying to encode " + self._spotify_data.album_art_filename)
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
    else:
      self.ids.input_artist.text = ''

    if self._audiofile.oldTags.albumartist:
      self.ids.input_albumartist.text = self._audiofile.oldTags.albumartist
    else:
      self.ids.input_albumartist.text = ''

    if self._audiofile.oldTags.album:
      self.ids.input_album.text = self._audiofile.oldTags.album
    else:
      self.ids.input_album.text = ''

    if self._audiofile.oldTags.title:
      self.ids.input_title.text = self._audiofile.oldTags.title
    else:
      self.ids.input_title.text = ''

    if self._audiofile.oldTags.date:
      self.ids.input_date.text = self._audiofile.oldTags.date
    else:
      self.ids.input_date.text = ''

    if self._audiofile.oldTags.genre:
      self.ids.input_genre.text = self._audiofile.oldTags.genre
    else:
      self.ids.input_genre.text = ''

    if self._audiofile.oldTags.comment:
      self.ids.input_comment.text = self._audiofile.oldTags.comment
    else:
      self.ids.input_comment.text = ''

    if self._audiofile.oldTags.lyrics:
      self.ids.input_lyrics.text = self._audiofile.oldTags.lyrics
    else:
      self.ids.input_lyrics.text = ''

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
  TagItApp().run()
