import os
import asyncio
import statistics
import json

from pubnub.callbacks import SubscribeCallback
from pubnub.enums import PNStatusCategory, PNOperationType
from pubnub.pnconfiguration import PNConfiguration
from pubnub.pubnub import PubNub

pnconfig = PNConfiguration()

pnconfig.subscribe_key = 'sub-c-78806dd4-42a6-11e4-aed8-02ee2ddab7fe'
pnconfig.uuid = 'myUniqueUUID'
pubnub = PubNub(pnconfig)

CHANNEL = 'pubnub-twitter'

SLIDING_AVERAGE_TWEETS = []

class Tweet:

    def __init__(self):
        self.created_at = created_at

def my_publish_callback(envelope, status):
    print('mpc')
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
    pubnub.add_listener(MySubscribeCallback())
    pubnub.subscribe().channels(CHANNEL).execute()

if __name__ == "__main__":
    asyncio.run(main())
    # main()