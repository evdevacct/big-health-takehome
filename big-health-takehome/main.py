import os
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
        print(message.message)
        bbox = message.message['place']['bounding_box']
        # if bbox['type'] != 'Polygon':
        with open('debug.json', 'w') as f:
            json.dump(message.message, f)
        center = coords_from_bounding_box(bbox)
        print(center)
        os._exit(0)

def coords_from_bounding_box(bbox):
    if bbox['type'] == 'Polygon':
        assert len(bbox['coordinates']) == 1
        polygon_coords = bbox['coordinates'][0]
        lat_total, lng_total = 0, 0
        for lat, lng in polygon_coords:
            lat_total += lat
            lng_total += lng
        point_count = len(polygon_coords)
        return lat_total / point_count, lng_total / point_count

pubnub.add_listener(MySubscribeCallback())

pubnub.subscribe().channels(CHANNEL).execute()