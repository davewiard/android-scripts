#!/usr/bin/env python3

import subprocess


packages = [
  'com.netease.eve.en',
  'com.hikvision.hikconnect',
]


def get_notifications():
  process = subprocess.run(['/data/data/com.termux/files/usr/libexec/termux-api', 'NotificationList'])
  return process.stdout


if __name__ == '__main__':
  result = get_notifications()
  print(result)
