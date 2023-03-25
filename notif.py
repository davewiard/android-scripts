#!/usr/bin/env python3

import os
import logging
import subprocess
import json


packageNames = [
  ('com.formagrid.airtable', 'airtable'),                          # Airtable
  ('com.alaskaairljnes.android', 'alaskaai'),                      # Alaska Airlines
  ('com.amazon.mp3', 'amazonmu'),                                  # Amazon Music
  ('com.amazon.mShop.android.shopping', 'amazonsh'),               # Amazon Shopping
  ('com.aa.android', 'american'),                                  # American Airlines
  ('com.apple.android.music', 'applemus'),                         # Apple Music
  ('com.authy.authy', 'authy'),                                    # Authy
  ('com.fillobotto.mp3tagger','automata'),                         # AutomaTag
  ('org.becu.androidapp', 'becu'),                                 # BECU
  ('blockpuzzle.jewelgames.jewelslegend', 'blockpuz'),             # Block Puzzle Legend
  ('com.bridgecitytools', 'bridgeci'),                             # Bridge City Tools
  ('com.sec.android.app.camera', 'camera'),                        # Camera
  ('com.android.chrome', 'chrome'),                                # Chrome
  ('com.citi.citimobile', 'citi'),                                 # Citi
  ('com.cnn.mobile.android.phone', 'cnn'),                         # CNN
  ('com.coinbase.android', 'coinbase'),                            # Coinbase
  ('com.samsung.android.app.contacts', 'contacts'),                # Contacts
  ('com.delta.mobile.android', 'deltaair'),                        # Delta Airlines
  ('com.discord', 'discord'),                                      # Discord
  ('com.disney.disneyplus', 'disneypl'),                           # Disney+
  ('app.edwardjones.mobile', 'edwardjo'),                          # Edward Jones
  ('com.netease.eve.en', 'eveechoe'),                              # EVE Echoes
  ('com.facebook.katana', 'facebook'),                             # Facebook
  ('com.facebook.orca', 'messenge'),                               # Facebook Messenger
  ('com.fedex.ida.android', 'fedex'),                              # FedEx
  ('com.square_enix.android.googleplay.FFVII', 'ffvii'),           # Final Fantasy VII
  ('com.fitbit.FitbitMobile', 'fitbit'),                           # Fitbit
  ('com.kajda.fuelio', 'fuelio'),                                  # Fuelio
  ('com.google.android.gm', 'gmail'),                              # Gmail
  ('com.playdemic.golf.android', 'golfclas'),                      # Golf Clash
  ('com.golfnow.android.teetimes', 'golfnow'),                     # GolfNow
  ('com.contorra.golfpad', 'golfpad'),                             # Golf Pad
  ('gonemad.gmmp', 'gonemad'),                                     # GoneMAD Music Player
  ('com.google.android.apps.authenticator2', 'googleau'),          # Google Authenticator
  ('com.google.android.apps.maps', 'googlema'),                    # Google Maps
  ('com.android.vending', 'googlepl'),                             # Google Play
  ('com.hawaiianairlines.app', 'hawaiian'),                        # Hawaiian Airlines
  ('com.hbo.hbonow', 'hbomax'),                                    # HBO MAX
  ('com.thehomedepot', 'homedepo'),                                # Home Depot
  ('com.hulu.plus', 'hulu'),                                       # hulu
  ('com.imdb.mobile', 'imdb'),                                     # IMDb
  ('com.kunzisoft.keepass.free', 'keepass'),                       # Keepass
  ('com.lowes.android', 'lowes'),                                  # Lowe's
  ('com.microsoft.mahjong', 'mahjong'),                            # Mahjong
  ('com.samsung.android.messaging', 'messages'),                   # Messages
  ('co.peeksoft.stocks', 'msp'),                                   # MSP
  ('com.netflix.mediaclient', 'netflix'),                          # Netflix
  ('com.okta.android.mobile.oktamobile', 'oktamobi'),              # Okta Mobile
  ('com.okta.android.auth', 'oktaveri'),                           # Okta Verify
  ('com.headcode.outgroceries', 'ourgroce'),                       # OurGroceries
  ('com.pagerduty.android', 'pagerdut'),                           # PagerDuty
  ('com.paypal.android.p2pmobile', 'paypal'),                      # PayPal
  ('com.samsung.android.dialer', 'phone'),                         # Phone
  ('com.politico.android', 'politico'),                            # POLITICO
  ('com.amazon.avod.thirdpartyclient', 'primevid'),                # Prime Video
  ('com.robinhood.android', 'robinhoo'),                           # Robinhood
  ('com.roku.remote', 'roku'),                                     # Roku
  ('com.schwab.mobile.retirement', 'schwab'),                      # Schwab
  ('com.solium.shareworks', 'sharewor'),                           # Shareworks
  ('com.shopify.arrive', 'shop'),                                  # Shop
  ('com.Slack', 'slack'),                                          # Slack
  ('pl.solidexplorer2', 'solidexp'),                               # Solid Explorer
  ('com.strava', 'strava'),                                        # Strava
  ('com.sillykat.eve.sweet', 'sweet'),                             # SWEET
  ('net.dinglisch.android.taskerm', 'tasker'),                     # Tasker
  ('com.termux', 'termux'),                                        # Termux
  ('com.fivemobile.thescore', 'thescore'),                         # theScore
  ('com.ultimatesoftware.ultipromobile', 'ukgpro'),                # UKG Pro
  ('com.ups.android.mobile', 'ups'),                               # UPS
  ('com.venmo', 'venmo'),                                          # Venmo
  ('com.wire', 'wire'),                                            # Wire
  ('com.peoplefun.wordcross', 'wordscap'),                         # Wordscapes
  ('com.peoplefun.wordsearch', 'wordsear'),                        # Word Search
  ('com.wyndhamhotelgroup.wyndhamrewards', 'wyndham'),             # Wyndham
  ('com.yahoo.mobile.client.android.fantasyfootball', 'yahoofan')  # Yahoo Fantasy
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

  for packageName, klwpVarName in packageNames:
    count = get_count(packageName, data)
    logging.info(packageName)
    logging.info(klwpVarName)
    logging.info(count)

    notificationCounts.append(packageName + ':' + klwpVarName + ':' + str(count))

  output = { "notifications": notificationCounts }
  print(json.dumps(output))
