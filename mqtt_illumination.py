#!/usr/bin/env python3
"""Test script to control illumination from a MQTT topic."""

import asyncio
import contextlib
import logging
import signal

import illumination as il

from mqtt import AsyncioClient

import rpi_ws281x as ws

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


def signal_handler(signum, frame):
    """Catch any interrupt signal and raise a KeyboardInterrupt.

    Useful for translating SIGINTs sent from other processes into a KeyboardInterrupt.
    """
    raise KeyboardInterrupt


class Illuminator(AsyncioClient):
    """Sets NeoPixel illumination based on messages from the broker."""

    def __init__(self, *args, **kwargs):
        """Initialize client state."""
        super().__init__(*args, **kwargs)
        self.lights = il.Illumination()
        self.modes = ['clear', 'wipe', 'theater', 'rainbow']
        self.mode_actions = {
            'clear': self.clear,
            'wipe': self.wipe,
            'theater': self.theater,
            'rainbow': self.rainbow
        }
        self.illumination_task = None

    def on_topic(self, client, userdata, msg):
        """Handle any messages from the broker on the preset topic."""
        mode_code = int(msg.payload)
        try:
            mode = self.modes[mode_code]
        except IndexError:
            logger.error('Unknown mode code: {}'.format(mode_code))
            mode = 'clear'
        logger.info('Setting illumination mode to: {}'.format(mode))
        if self.illumination_task is not None:
            self.illumination_task.cancel()
        self.illumination_task = self.loop.create_task(self.mode_actions[mode]())

    def add_topic_handlers(self):
        """Add any topic handler message callbacks as needed."""
        self.client.message_callback_add(topic, self.on_topic)

    async def wipe(self):
        while True:
            await self.lights.color_wipe(ws.Color(0, 0, 255), wait_ms=20)
            await self.lights.color_wipe(ws.Color(0, 0, 0), wait_ms=20)

    async def theater(self):
        while True:
            await self.lights.theater_chase(ws.Color(0, 0, 255), wait_ms=200)

    async def rainbow(self):
        while True:
            await self.lights.rainbow_cycle(wait_ms=2)

    async def clear(self):
        await self.lights.clear()

    async def on_quit(self):
        """When the client quits, handle it."""
        await self.clear()


if __name__ == '__main__':
    signal.signal(signal.SIGINT, signal_handler)

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
        pending = asyncio.Task.all_tasks()
        for task in pending:
            task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                loop.run_until_complete(task)
    finally:
        loop.close()
    logger.info('Finished!')
