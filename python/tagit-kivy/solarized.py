#!/usr/bin/env python3

class Solarized:
  ''' Class for defining Solarized colors in different formats'''
  DECIMAL = 'decimal'
  HEX = 'hex'
  RGB = 'rgb'

  BASE03 = 'base03'
  BASE02 = 'base02'
  BASE01 = 'base01'
  BASE00 = 'base00'
  BASE0 = 'base0'
  BASE1 = 'base1'
  BASE2 = 'base2'
  BASE3 = 'base3'
  YELLOW = 'yellow'
  ORANGE = 'orange'
  RED = 'red'
  MAGENTA = 'magenta'
  VIOLET = 'violet'
  BLUE = 'blue'
  CYAN = 'cyan'
  GREEN = 'green'
  

  _valid_names = [
    'base03',
    'base02',
    'base01',
    'base00',
    'base0',
    'base1',
    'base2',
    'base3',
    'yellow',
    'orange',
    'red',
    'magenta',
    'violet',
    'blue',
    'cyan',
    'green'
  ]

  _decimal = {
    'base03' : [  0/255,  43/255,  54/255, 1],
    'base02' : [ 54/255,  66/255, 192/255, 1],
    'base01' : [110/255, 117/255, 194/255, 1],
    'base00' : [123/255, 131/255, 195/255, 1],
    'base0'  : [131/255, 148/255, 150/255, 1],
    'base1'  : [147/255, 161/255, 161/255, 1],
    'base2'  : [238/255, 232/255, 213/255, 1],
    'base3'  : [253/255, 246/255, 227/255, 1],
    'yellow' : [181/255, 137/255,   0/255, 1],
    'orange' : [203/255,  75/255,  22/255, 1],
    'red'    : [220/255,  50/255,  47/255, 1],
    'magenta': [211/255,  54/255, 130/255, 1],
    'violet' : [108/255, 113/255, 196/255, 1],
    'blue'   : [ 38/255, 139/255, 210/255, 1],
    'cyan'   : [ 42/255, 161/255, 152/255, 1],
    'green'  : [133/255, 153/255,   0/255, 1]
  }
  
  _hex = {
    'base03' : '#002b36',
    'base02' : '#073642',
    'base01' : '#586e75',
    'base00' : '#657b83',
    'base0'  : '#839496',
    'base1'  : '#93a1a1',
    'base2'  : '#eee8d5',
    'base3'  : '#fdf6e3',
    'yellow' : '#b58900',
    'orange' : '#cb4b16',
    'red'    : '#dc322f',
    'magenta': '#d33682',
    'violet' : '#6c71c4',
    'blue'   : '#268bd2',
    'cyan'   : '#2aa198',
    'green'  : '#859900'
  }
  
  _rgb = {
    'base03' : [  0,  43,  54],
    'base02' : [ 54,  66, 192],
    'base01' : [110, 117, 194],
    'base00' : [123, 131, 195],
    'base0'  : [131, 148, 150],
    'base1'  : [147, 161, 161],
    'base2'  : [238, 232, 213],
    'base3'  : [253, 246, 227],
    'yellow' : [181, 137,   0],
    'orange' : [203,  75,  22],
    'red'    : [220,  50,  47],
    'magenta': [211,  54, 130],
    'violet' : [108, 113, 196],
    'blue'   : [ 38, 139, 210],
    'cyan'   : [ 42, 161, 152],
    'green'  : [133, 153,   0]
  }
  
  def __init__(self):
    pass

  @property
  def decimal(self):
    return self._decimal

  @property
  def hex(self):
    return self._hex

  @property
  def rgb(self):
    return self._rgb

  def is_name_valid(self, name):
    return (name in self._valid_names)

  def get_color(self, name, format = 'hex'):
    ''' Returns the requested color in the requested format '''
    if not self.is_name_valid(name):
      return None

    if format == self.DECIMAL:
      return self._decimal[name]

    if format == self.HEX:
      return self._hex[name]

    if format == self.RGB:
      return self._rgb[name]

    return None
