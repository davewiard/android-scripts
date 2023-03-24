#!/usr/bin/env python3

import os
import logging
import subprocess
import json


packageNames = [
  'com.formagrid.airtable',                           # Airtable
  'com.amazon.mp3',                                   # Amazon Music
  'com.apple.android.music',                          # Apple Music
  'com.authy.authy',                                  # Authy
  'com.fillobotto.mp3tagger',                         # AutomaTag
  'org.becu.androidapp',                              # BECU
  'blockpuzzle.jewelgames.jewelslegend',              # Block Puzzle Legend
  'com.sec.android.app.camera',                       # Camera
  'com.android.chrome',                               # Chrome
  'com.citi.citimobile',                              # Citi
  'com.cnn.mobile.android.phone',                     # CNN
  'com.coinbase.android',                             # Coinbase
  'com.samsung.android.app.contacts',                 # Contacts
  'com.discord',                                      # Discord
  'com.disney.disneyplus',                            # Disney+
  'app.edwardjones.mobile',                           # Edward Jones
  'com.netease.eve.en',                               # EVE Echoes
  'com.facebook.katana',                              # Facebook
  'com.facebook.orca',                                # Facebook Messenger
  'com.square_enix.android.googleplay.FFVII',         # Final Fantasy VII
  'com.fitbit.FitbitMobile',                          # Fitbit
  'com.kajda.fuelio',                                 # Fuelio
  'com.google.android.gm',                            # Gmail
  'com.playdemic.golf.android',                       # Golf Clash
  'com.golfnow.android.teetimes',                     # GolfNow
  'com.contorra.golfpad',                             # Golf Pad
  'gonemad.gmmp',                                     # GoneMAD Music Player
  'com.google.android.apps.authenticator2',           # Google Authenticator
  'com.android.vending',                              # Google Play
  'com.hbo.hbonow',                                   # HBO MAX
  'com.hulu.plus',                                    # hulu
  'com.imdb.mobile',                                  # IMDb
  'com.kunzisoft.keepass.free',                       # Keepass
  'com.microsoft.mahjong',                            # Mahjong
  'com.samsung.android.messaging',                    # Messages
  'co.peeksoft.stocks',                               # MSP
  'com.netflix.mediaclient',                          # Netflix
  'com.okta.android.mobile.oktamobile',               # Okta Mobile
  'com.okta.android.auth',                            # Okta Verify
  'com.headcode.outgroceries',                        # OurGroceries
  'com.pagerduty.android',                            # PagerDuty
  'com.paypal.android.p2pmobile',                     # PayPal
  'com.samsung.android.dialer',                       # Phone
  'com.politico.android',                             # POLITICO
  'com.amazon.avod.thirdpartyclient',                 # Prime Video
  'com.robinhood.android',                            # Robinhood
  'com.roku.remote',                                  # Roku
  'com.schwab.mobile.retirement',                     # Schwab
  'com.solium.shareworks',                            # Shareworks
  'com.Slack',                                        # Slack
  'pl.solidexplorer2',                                # Solid Explorer
  'com.strava',                                       # Strava
  'com.sillykat.eve.sweet',                           # SWEET
  'net.dinglisch.android.taskerm',                    # Tasker
  'com.termux',                                       # Termux
  'com.fivemobile.thescore',                          # theScore
  'com.ultimatesoftware.ultipromobile',               # UKG Pro
  'com.venmo',                                        # Venmo
  'com.wire',                                         # Wire
  'com.peoplefun.wordcross',                          # Wordscapes
  'com.peoplefun.wordsearch',                         # Word Search
  'com.yahoo.mobile.client.android.fantasyfootball'   # Yahoo Fantasy
]


def get_count(packageName, data):
  count = 0
  for item in data:
    logging.debug(item)
    if item['packageName'] == packageName:
      count = count + 1

  return count


if __name__ == '__main__':
  logfile = '.'.join([os.path.splitext(__file__)[0], 'log'])
  if os.getenv('DEBUG'):
    logging.basicConfig(filename = logfile, filemode = 'w', level = logging.DEBUG)
  else:
    logging.basicConfig(filename = logfile, filemode = 'w', level = logging.INFO)

  process = subprocess.run(['/data/data/com.termux/files/usr/libexec/termux-api', 'NotificationList'], capture_output=True, text=True)
  data = json.loads(process.stdout)
  logging.debug(data)

  notificationCounts = []

  for packageName in packageNames:
    count = get_count(packageName, data)
    logging.info(packageName)
    logging.info(count)

    notificationCounts.append({packageName: count})

  logging.info(notificationCounts)
