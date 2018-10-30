#!/usr/bin/env python3
"""Test script to control illumination from a MQTT topic."""

import asyncio
import contextlib
import logging
import logging.config
import signal

from intervention_client import illumination as il
from intervention_client.mqtt import AsyncioClient

import rpi_ws281x as ws

# Program parameters
hostname = 'm15.cloudmqtt.com'
port = 16076
username = 'lpkbaxec'
password = 'limdi7J_A3Tc'
illumination_topic = 'testing-illumination'
control_topic = 'testing-control'

# Set up logging
logging.config.dictConfig({
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'f': {
            'format': '%(asctime)s %(name)-12s %(levelname)-8s %(message)s'
        }
    },
    'handlers': {
        'h': {
            'class': 'logging.StreamHandler',
            'formatter': 'f',
            'level': logging.INFO
        }
    },
    'root': {
        'handlers': ['h'],
        'level': logging.INFO
    }
})
logger = logging.getLogger(__name__)


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
        self.modes = ['clear', 'breathe', 'wipe', 'theater', 'rainbow']
        self.mode_actions = {
            'clear': self.clear,
            'breathe': self.breathe,
            'wipe': self.wipe,
            'theater': self.theater,
            'rainbow': self.rainbow
        }
        self.illumination_task = None

    def on_connect(self, client, userdata, flags, rc):
        """When the client connects, handle it."""
        self.set_illumination_mode('clear')
        super().on_connect(client, userdata, flags, rc)
        self.client.publish('connect', 'illumination client', qos=2)

    def on_disconnect(self, client, userdata, rc):
        """When the client disconnects, handle it."""
        self.set_illumination_mode('breathe')
        super().on_disconnect(client, userdata, rc)

    def on_control_topic(self, client, userdata, msg):
        """Handle any program control messages."""
        command = msg.payload.decode('utf-8')
        if command == 'restart':
            logger.info('Restarting...')
            process = self.loop.create_task(asyncio.create_subprocess_exec(
                'shutdown', '-r', 'now',
                stdout=asyncio.subprocess.PIPE
            ))

    def on_illumination_topic(self, client, userdata, msg):
        """Handle any illumination messages."""
        mode_code = int(msg.payload)
        try:
            mode = self.modes[mode_code]
        except IndexError:
            logger.error('Unknown mode code: {}'.format(mode_code))
            mode = 'clear'
        logger.info('Setting illumination mode to: {}'.format(mode))
        self.set_illumination_mode(mode)

    def add_topic_handlers(self):
        """Add any topic handler message callbacks as needed."""
        self.client.message_callback_add(control_topic, self.on_control_topic)
        self.client.message_callback_add(illumination_topic, self.on_illumination_topic)

    async def clear(self):
        try:
            self.lights.clear()
        except KeyboardInterrupt:
            self.lights.clear()

    async def breathe(self):
        try:
            while True:
                await self.lights.breathe(255)
        except KeyboardInterrupt:
            pass

    async def wipe(self):
        try:
            while True:
                await self.lights.color_wipe(ws.Color(0, 0, 255), wait_ms=40)
                await self.lights.color_wipe(ws.Color(0, 0, 0), wait_ms=40)
        except KeyboardInterrupt:
            pass

    async def theater(self):
        try:
            while True:
                await self.lights.theater_chase(ws.Color(0, 0, 255), wait_ms=200)
        except KeyboardInterrupt:
            pass

    async def rainbow(self):
        try:
            while True:
                await self.lights.rainbow_cycle(wait_ms=2)
        except KeyboardInterrupt:
            pass

    def set_illumination_mode(self, mode):
        if self.illumination_task is not None:
            self.illumination_task.cancel()
        self.illumination_task = self.loop.create_task(self.mode_actions[mode]())

    def on_run(self):
        """When the client start the run loop, handle it."""
        self.set_illumination_mode('breathe')

    def on_quit(self):
        """When the client quits the run loop, handle it."""
        if self.illumination_task is not None:
            self.illumination_task.cancel()


if __name__ == '__main__':
    signal.signal(signal.SIGINT, signal_handler)

    logger.info('Starting client...')
    loop = asyncio.get_event_loop()
    mqttc = Illuminator(
        loop, hostname, port, username=username, password=password,
        topics={
            illumination_topic: 2,
            control_topic: 2
        }
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
            loop.run_until_complete(asyncio.gather(*pending))
    finally:
        loop.close()
        mqttc.lights.clear()
    logger.info('Finished!')
