#!/usr/bin/env python3
"""Test script to control illumination from a MQTT topic."""

import asyncio
import contextlib
import json
import logging
import logging.config
import signal

from intervention_client import illumination as il
from intervention_client import config
from intervention_client.mqtt import AsyncioClient

import rpi_ws281x as ws

# Program parameters
usb_path = '/media/usb0/settings.json'
configuration = config.load_config(usb_path)
pi_username = configuration['pi username']
hostname = configuration['hostname']
port = configuration['port']
username = configuration['username']
password = configuration['password']
illumination_topic = 'illumination'
deploy_topic = 'deploy'
message_encoding = 'utf-8'

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
        self.mode_handlers = {
            'clear': self.clear,
            'breathe': self.breathe,
            'wipe': self.wipe,
            'theater': self.theater,
            'rainbow': self.rainbow
        }
        self.illumination_task = None
        self.illumination_params = None

    def on_connect(self, client, userdata, flags, rc):
        """When the client connects, handle it."""
        self.set_illumination({'mode': 'clear'})
        super().on_connect(client, userdata, flags, rc)
        self.client.publish('connect', 'illumination client', qos=2)

    def on_disconnect(self, client, userdata, rc):
        """When the client disconnects, handle it."""
        self.set_illumination({'mode': 'breathe'})
        super().on_disconnect(client, userdata, rc)

    def on_deploy_topic(self, client, userdata, msg):
        """Handle any device deployment messages."""
        command = msg.payload.decode(message_encoding)
        if command == 'restart':
            self.loop.create_task(self.restart())
        elif command == 'git pull':
            self.loop.create_task(self.git_pull())

    async def restart(self):
        logger.info('Restarting...')
        process = await asyncio.create_subprocess_exec(
            'systemctl', 'reboot',
            stdout=asyncio.subprocess.PIPE
        )

    async def git_pull(self):
        logger.info('Updating local repo...')
        process = await asyncio.create_subprocess_exec(
                'sudo', '-u', pi_username, 'git', 'pull',
                stdout=asyncio.subprocess.PIPE
            )
        await process.communicate()
        await self.restart()

    def on_illumination_topic(self, client, userdata, msg):
        """Handle any illumination messages."""
        payload = msg.payload.decode(message_encoding)
        try:
            illumination_params = json.loads(payload)
        except json.JSONDecodeError:
            logger.error('Malformed illumination parameters: {}'.format(payload))
            return
        try:
            mode = illumination_params['mode']
            mode_handler = self.mode_handlers[mode]
        except (KeyError, IndexError):
            logger.error('Unknown/missing illumination mode: {}'.format(payload))
            return
        logger.info('Setting illumination: {}'.format(payload))
        self.set_illumination(illumination_params)

    def add_topic_handlers(self):
        """Add any topic handler message callbacks as needed."""
        self.client.message_callback_add(deploy_topic, self.on_deploy_topic)
        self.client.message_callback_add(illumination_topic, self.on_illumination_topic)

    async def clear(self, params):
        try:
            self.lights.clear()
        except KeyboardInterrupt:
            self.lights.clear()

    async def breathe(self, params):
        intensity = params.get('intensity', 255)
        wait_ms = params.get('wait_ms', 2)
        try:
            while True:
                await self.lights.breathe(intensity, wait_ms=wait_ms)
        except KeyboardInterrupt:
            pass

    async def wipe(self, params):
        loop = params.get('loop', True)
        colors = params.get('colors', [])
        if len(colors) < 1:
            colors.append({
                'red': 0, 'green': 0, 'blue': 255,
                'hold': 0, 'wait_ms': 40
            })
        if loop and len(colors) < 2:
            colors.append({
                'red': 0, 'green': 0, 'blue': 0,
                'hold': 0, 'wait_ms': 40
            })
        led_colors = [
            (
                ws.Color(
                    color.get('red', 0),
                    color.get('green', 0),
                    color.get('blue', 0)
                ),
                color.get('wait_ms', 40),
                color.get('hold_ms', 0)
            )
            for color in colors
        ]
        try:
            while True:
                for (led_color, wait_ms, hold_duration) in led_colors:
                    await self.lights.color_wipe(led_color, wait_ms=wait_ms)
                    await asyncio.sleep(hold_duration / 1000.0)
                if not loop:
                    break
        except KeyboardInterrupt:
            pass

    async def theater(self, params):
        color = params.get('color', {'red': 0, 'green': 0, 'blue': 255})
        color = ws.Color(
            color.get('red', 0),
            color.get('green', 0),
            color.get('blue', 0)
        )
        wait_ms = params.get('wait_ms', 200)
        try:
            while True:
                await self.lights.theater_chase(color, wait_ms=wait_ms)
        except KeyboardInterrupt:
            pass

    async def rainbow(self, params):
        wait_ms = params.get('wait_ms', 2)
        try:
            while True:
                await self.lights.rainbow_cycle(wait_ms=wait_ms)
        except KeyboardInterrupt:
            pass

    def set_illumination(self, illumination_params):
        if self.illumination_task is not None:
            self.illumination_task.cancel()
        mode = illumination_params['mode']
        self.illumination_params = illumination_params
        print(illumination_params)
        self.illumination_task = self.loop.create_task(
            self.mode_handlers[mode](illumination_params)
        )

    def on_run(self):
        """When the client start the run loop, handle it."""
        self.set_illumination({'mode': 'breathe'})

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
            deploy_topic: 2
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
