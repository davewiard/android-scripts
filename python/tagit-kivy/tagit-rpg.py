#!/usr/bin/env python3

import sys
import subprocess

def update_replaygain(filename):
  print('Applying ReplayGain tags...')
  process = subprocess.run(['r128gain', '-v', 'warning', filename], capture_output=True, text=True)
  if process.returncode != 0:
    print('Failed to upsert replaygain tags')
    print('----')
    print(process.stdout)
    print('----')
    print(process.stderr)
    print('----')


if __name__ == '__main__':
  filename = sys.argv[1]
  print('Scanning ' + filename)
  update_replaygain(filename)
