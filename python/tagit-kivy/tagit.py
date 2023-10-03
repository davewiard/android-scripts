#!/usr/bin/env python3

from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.gridlayout import GridLayout

class TagItLayoutLandscape(GridLayout):
  def __init__(self, **kwargs):
    super(TagItLayoutLandscape, self).__init__(**kwargs)

class TagItApp(App):
  def build(self):
    return TagItLayoutLandscape()

if __name__ == '__main__':
  TagItApp().run()
