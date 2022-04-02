#!/usr/bin/python

import pywemo
import sys
import logging
import shlex
import subprocess


def send_status(device, action, value = None):
    device_name = device.basicevent.GetFriendlyName()['FriendlyName']
    
    device_name_param = "-e device_name '{}'".format(device_name)
    action_param = "-e action '{}'".format(action)

    cmd = "/data/data/com.termux/files/usr/bin/am broadcast"
    user = "--user 0"
    act = "-a net.dinglish.tasker.wemo"
    
    full_cmd = "{} {} {} {} {}".format(cmd, user, act, device_name_param, action_param)
    full_cmd = "{} -e value '{}'".format(full_cmd, value if value else ' ')
        
    args = shlex.split(full_cmd)
    subprocess.Popen(args)


def off(device):
    device.off()
    send_status(device, 'off')


def on(device):
    device.on()
    send_status(device, 'on')


def set_brightness(device, brightness):
    if brightness < 1:
        brightness = 0
    elif brightness > 100:
        brightness = 100

    logging.debug('setting brightness to {}'.format(brightness))
    device.set_brightness(brightness)
    send_status(device, 'brightness', brightness)


def show_usage():
    print('wemo-control.py <name> <action> [value]')
    print('    name      device friendly name')
    print('    action    brightness, off, on')
    print('    value     optional value associated with action')


if __name__ == '__main__':
    logging.basicConfig(filename='wemo-control.log', filemode='w', level=logging.DEBUG)
    
    if len(sys.argv) < 3:
        show_usage()
        exit()

    device_name = sys.argv[1]
    logging.debug('Device Name: {}'.format(device_name))

    action = sys.argv[2]
    logging.debug('Action     : {}'.format(action))

    value = sys.argv[3] if len(sys.argv) > 3 else None
    logging.debug('Value      : {}'.format(value))

    devices = pywemo.discover_devices()
    device = [d for d in devices if d.basicevent.GetFriendlyName()['FriendlyName'] == device_name]
    if len(device) == 0:
        logging.debug('Device \'{}\' not found'.format(device_name))
        exit()
        
    send_status(device[0], action, value)

    if action == 'brightness':
        set_brightness(device[0], int(value))
    elif action == 'off':
        off(device[0])
    elif action == 'on':
        on(device[0])
