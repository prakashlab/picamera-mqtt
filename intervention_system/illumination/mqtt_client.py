"""Test script to control illumination from a MQTT topic."""

import asyncio
import json
import logging
import logging.config
import os

from intervention_system.deploy import (
    settings_key_path, client_config_plain_path, client_config_cipher_path
)
from intervention_system.mqtt_clients import AsyncioClient, message_string_encoding
from intervention_system.protocol import illumination_topic, deployment_topic
from intervention_system.util import config
from intervention_system.util.async import (
    register_keyboard_interrupt_signals, run_function
)
from intervention_system.util.logging import logging_config

# Set up logging
logging.config.dictConfig(logging_config)
logger = logging.getLogger(__name__)

# Configure configuration file loading
use_encrypted_settings = True

# Configure messaging
topics = {
    illumination_topic: 2,
    deployment_topic: 2
}


class Illuminator(AsyncioClient):
    """Sets NeoPixel illumination based on messages from the broker."""

    def __init__(self, *args, pi_username='pi', **kwargs):
        """Initialize client state."""
        super().__init__(*args, **kwargs)

        self.init_illumination()
        self.mode_handlers = {
            'clear': self.clear,
            'breathe': self.breathe,
            'wipe': self.wipe,
            'theater': self.theater,
            'rainbow': self.rainbow
        }
        self.illumination_task = None
        self.illumination_params = None

        self.pi_username = pi_username

    def init_illumination(self):
        """Initialize illumination support."""
        # Only import if needed
        from intervention_system.illumination import illumination as il

        self.lights = il.Illumination()

    def on_connect(self, client, userdata, flags, rc):
        """When the client connects, handle it."""
        self.set_illumination({'mode': 'clear'})
        super().on_connect(client, userdata, flags, rc)
        self.client.publish('connect', 'illumination client', qos=2)

    def on_disconnect(self, client, userdata, rc):
        """When the client disconnects, handle it."""
        if rc != 0:
            self.set_illumination({'mode': 'breathe'})
        super().on_disconnect(client, userdata, rc)

    def on_deployment_topic(self, client, userdata, msg):
        """Handle any device deployment messages."""
        command = msg.payload.decode(message_string_encoding)
        if command == 'restart':
            self.loop.create_task(self.restart())
        elif command == 'shutdown':
            self.loop.create_task(self.shutdown())
        elif command == 'git pull':
            self.loop.create_task(self.git_pull())

    async def restart(self):
        """Trigger a system restart."""
        logger.info('Restarting...')
        await asyncio.create_subprocess_exec(
            'systemctl', 'reboot',
            stdout=asyncio.subprocess.PIPE
        )

    async def shutdown(self):
        """Trigger a system shutdown."""
        logger.info('Shutting down...')
        await asyncio.create_subprocess_exec(
            'systemctl', 'poweroff',
            stdout=asyncio.subprocess.PIPE
        )

    async def git_pull(self):
        """Trigger a repository update and subsequent system restart."""
        logger.info('Updating local repo...')
        process = await asyncio.create_subprocess_exec(
                'sudo', '-u', self.pi_username, 'git', 'pull',
                stdout=asyncio.subprocess.PIPE
            )
        await process.communicate()
        await self.restart()

    def on_illumination_topic(self, client, userdata, msg):
        """Handle any illumination messages."""
        payload = msg.payload.decode(message_string_encoding)
        try:
            illumination_params = json.loads(payload)
        except json.JSONDecodeError:
            logger.error('Malformed illumination parameters: {}'.format(payload))
            return
        try:
            mode = illumination_params['mode']
            self.mode_handlers[mode]
        except (KeyError, IndexError):
            logger.error('Unknown/missing illumination mode: {}'.format(payload))
            return
        self.set_illumination(illumination_params)

    def add_topic_handlers(self):
        """Add any topic handler message callbacks as needed."""
        self.client.message_callback_add(deployment_topic, self.on_deployment_topic)
        self.client.message_callback_add(illumination_topic, self.on_illumination_topic)

    async def clear(self, params):
        """Clear the lights."""
        try:
            self.lights.clear()
        except KeyboardInterrupt:
            self.lights.clear()

    async def breathe(self, params):
        """Breathe the lights between white and dark."""
        intensity = params.get('intensity', 255)
        wait_ms = params.get('wait_ms', 2)
        try:
            while True:
                await self.lights.breathe(intensity, wait_ms=wait_ms)
        except KeyboardInterrupt:
            pass

    async def wipe(self, params):
        """Wipe the lights with colors."""
        # Only import if needed
        import rpi_ws281x as ws

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
        """Run a theater marquee on the lights."""
        # Only import if needed
        import rpi_ws281x as ws

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
        """Move a rainbow across the lights."""
        wait_ms = params.get('wait_ms', 2)
        try:
            while True:
                await self.lights.rainbow_cycle(wait_ms=wait_ms)
        except KeyboardInterrupt:
            pass

    def set_illumination(self, illumination_params):
        """Set the lights to some illumination."""
        logger.info('Setting illumination: {}'.format(illumination_params))
        if self.illumination_task is not None:
            self.illumination_task.cancel()
        mode = illumination_params['mode']
        self.illumination_params = illumination_params
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
    register_keyboard_interrupt_signals()

    # Load configuration
    if use_encrypted_settings:
        config_path = client_config_cipher_path
        keyfile_path = settings_key_path
    else:
        config_path = client_config_plain_path
        keyfile_path = None
    configuration = config.config_load(config_path, keyfile_path=keyfile_path)

    logger.info('Starting client...')
    loop = asyncio.get_event_loop()
    mqttc = Illuminator(
        loop, **configuration['broker'], **configuration['deploy'],
        topics=topics
    )
    run_function(mqttc.run)
    mqttc.lights.clear()
    logger.info('Finished!')
