#!/usr/bin/env python3

from collections import OrderedDict
import subprocess
import json


packageNames = [
  'com.google.gmail',
  'com.robinhood',
  'com.thescore'
]


def get_count(packageName, data):
  count = 0
  for item in data:
    if item['packageName'] == packageName:
      count = count + 1

  return count


if __name__ == '__main__':
  with open('./notif.json', 'r') as f:
    data = json.load(f)

  #result = subprocess.run(['/data/data/com.termux/files/usr/libexec/termux-api', 'NotifiactionList'])

  notificationCounts = []

  for packageName in packageNames:
    count = get_count(packageName, data)
    print(packageName)
    print(count)

    notificationCounts.append({packageName: count})

  print(notificationCounts)
