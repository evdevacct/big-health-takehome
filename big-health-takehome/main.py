import os
import sys
import argparse
import requests
import threading
from datetime import datetime
import dateutil.parser
import statistics
import json
from concurrent.futures import ThreadPoolExecutor
from pubnub.callbacks import SubscribeCallback
from pubnub.enums import PNStatusCategory, PNOperationType
from pubnub.pnconfiguration import PNConfiguration
from pubnub.pubnub import PubNub

pnconfig = PNConfiguration()

with open(os.path.join('..', '.env.json')) as f:
    CONFIG = json.load(f)
pnconfig.subscribe_key = CONFIG['PUBNUB_SUB_KEY']
pnconfig.uuid = 'myUniqueUUID'
pubnub = PubNub(pnconfig)
AVERAGES_FILENAME = os.path.join('..', 'averages.txt')
TEMPS_FILENAME = os.path.join('..', 'temps.txt')


CHANNEL = 'pubnub-twitter'
FIRST_TWEET = True
CALCULATOR = None

class SlidingAverageCalculator:

    def __init__(self, limit):
        self.previous_vals = []
        self.limit = limit

    def add_temp(self, temp):
        '''
        Naive implementation. Assuming tweets are coming in order for now. In
        the future could track previous averages so don't need to perform linear
        sum operation each time.
        '''
        self.previous_vals.append(temp)
        if len(self.previous_vals) > self.limit:
            self.previous_vals.pop(0)
        return statistics.mean(self.previous_vals)

def create_args(args):
    parser = argparse.ArgumentParser()
    parser.add_argument('n', type=int, help='Number of tweets to average')
    return parser.parse_args(args)

def my_publish_callback(envelope, status):
    # Check whether request successfully completed or not
    if not status.is_error():
        pass  # Message successfully published to specified channel.
    else:
        pass  # Handle message publish error. Check 'category' property to find out possible issue
        # because of which request did fail.
        # Request can be resent using: [status retry];


class MySubscribeCallback(SubscribeCallback):
    def presence(self, pubnub, presence):
        pass  # handle incoming presence data

    def status(self, pubnub, status):
        if status.category == PNStatusCategory.PNUnexpectedDisconnectCategory:
            pass  # This event happens when radio / connectivity is lost

        elif status.category == PNStatusCategory.PNConnectedCategory:
            # Connect event. You can do stuff like publish, and know you'll get it.
            # Or just use the connected event to confirm you are subscribed for
            # UI / internal notifications, etc
            pubnub.publish().channel(CHANNEL).message('Hello world!').pn_async(my_publish_callback)
        elif status.category == PNStatusCategory.PNReconnectedCategory:
            pass
            # Happens as part of our regular operation. This event happens when
            # radio / connectivity is lost, then regained.
        elif status.category == PNStatusCategory.PNDecryptionErrorCategory:
            pass
            # Handle message decryption error. Probably client configured to
            # encrypt messages and on live data feed it received plain text.

    def message(self, pubnub, message):
        # Handle new message stored in message.message
        new_tweet_pipeline(message.message, CALCULATOR)

def new_tweet_pipeline(message, calculator):
    # lat, lng
    coords = coords_from_message(message)
    created_at = dateutil.parser.parse(message['created_at'])
    temp_f = get_weather(coords)
    avg = calculator.add_temp(temp_f)
    write_output(temp_f, avg)

def get_weather(coords):
    coords_str = f'{coords[0]},{coords[1]}'
    resp = requests.get(f'https://api.weatherapi.com/v1/current.json?key={CONFIG["WEATHER_API_KEY"]}&q={coords_str}')
    body = resp.json()
    temp = body['current']['temp_f']
    return temp

def coords_from_message(message):
    if message['coordinates']:
        assert message['coordinates']['type'] == 'Point'
        lng, lat = message['coordinates']['coordinates']
        return lat, lng
    bbox = message['place']['bounding_box']
    if bbox['type'] == 'Polygon':
        assert len(bbox['coordinates']) == 1
        polygon_coords = bbox['coordinates'][0]
        lat_total, lng_total = 0, 0
        for lng, lat in polygon_coords:
            lng_total += lng
            lat_total += lat
        point_count = len(polygon_coords)
        return lat_total / point_count, lng_total / point_count

def write_output(temp, avg):
    global FIRST_TWEET
    first_tweet = FIRST_TWEET
    FIRST_TWEET = False
    with open(AVERAGES_FILENAME, 'a') as avg_file, open(TEMPS_FILENAME, 'a') as temp_file:
        if not first_tweet:
            temp_file.write('\n')
            avg_file.write('\n')
        temp_file.write(str(temp))
        avg_file.write(str(avg))

def main():
    # pass args to make function testable
    args = create_args(sys.argv[1:])
    if not 2 <= args.n <= 100:
        raise RuntimeError('Expecting n between 2 and 100')
    global CALCULATOR
    CALCULATOR = SlidingAverageCalculator(args.n)
    # Create stream files
    with open(AVERAGES_FILENAME, 'w'), open(TEMPS_FILENAME, 'w'):
        pass
    pubnub.add_listener(MySubscribeCallback())
    pubnub.subscribe().channels(CHANNEL).execute()

if __name__ == "__main__":
    main()