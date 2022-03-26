#!/usr/bin/env python3

import pywemo
import sys

def show_usage():
    print('wemo-control.py <name> <action> [value]')

if __name__ == '__main__':
    if len(sys.argv) < 3:
        show_usage()
        exit()

    device_name = sys.argv[1]
    print(device_name)

    action = sys.argv[2]
    print(action)

    if len(sys.argv) > 3:
        value = sys.argv[3]
        print(value)

    devices = pywemo.discover_devices()
    for device in devices:
        if device.basicevent.GetFriendlyName()['FriendlyName'] == device_name:
            print(device.basicevent.GetFriendlyName()['FriendlyName'])
