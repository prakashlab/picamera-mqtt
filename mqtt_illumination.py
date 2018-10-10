#!/usr/bin/env python3
"""Test script to control illumination from a MQTT topic."""

import asyncio
import contextlib
import logging

from mqtt import AsyncioClient

# Program parameters
hostname = 'm15.cloudmqtt.com'
port = 16076
username = 'lpkbaxec'
password = 'limdi7J_A3Tc'
topic = 'testing-illumination'

# Set up logging
logger = logging.getLogger(__name__)
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)


class Illuminator(AsyncioClient):
    """Sets NeoPixel illumination based on messages from the broker."""

    def __init__(self, *args, **kwargs):
        """Initialize client state."""
        super().__init__(*args, **kwargs)

    def on_topic(self, client, userdata, msg):
        """Handle any messages from the broker on the preset topic."""
        logger.info('Received illumination control message: {}'.format(msg.payload))

    def add_topic_handlers(self):
        """Add any topic handler message callbacks as needed."""
        self.client.message_callback_add(topic, self.on_topic)


if __name__ == '__main__':
    logger.info('Starting client...')
    loop = asyncio.get_event_loop()
    mqttc = Illuminator(
        loop, hostname, port, username=username, password=password, topics=[topic]
    )
    task = loop.create_task(mqttc.run())
    try:
        loop.run_until_complete(task)
    except KeyboardInterrupt:
        logger.info('Quitting...')
        task.cancel()
        with contextlib.suppress(asyncio.CancelledError):
            loop.run_until_complete(task)
    finally:
        loop.close()
    logger.info('Finished!')
