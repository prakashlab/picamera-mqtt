"""Test script to control illumination from a MQTT topic."""

import asyncio
import contextlib
import logging
import logging.config
import os
import signal

from intervention_client import config
from intervention_client.mqtt_illumination import (
    Illuminator,
    deploy_topic, illumination_topic,
    logging_config,
    repo_path,
    signal_handler
)

# Set up logging
logging.config.dictConfig(logging_config)
logger = logging.getLogger(__name__)


class MockIlluminator(Illuminator):
    """Sets NeoPixel illumination based on messages from the broker."""

    def init_illumination(self):
        """Initialize illumination support."""
        pass

    async def restart(self):
        """Trigger a system restart."""
        logger.info('Mock restarting (nop)...')

    async def shutdown(self):
        """Trigger a system shutdown."""
        logger.info('Mock shutting down (disconnecting)...')
        raise KeyboardInterrupt

    async def git_pull(self):
        """Trigger a repository update and subsequent system restart."""
        logger.info('Mock updating local repo (nop)...')

    def set_illumination(self, illumination_params):
        """Set the lights to some illumination."""
        logger.info('Mock setting lights to: {}'.format(illumination_params))


if __name__ == '__main__':
    # Config file paths
    config_path = os.path.join(repo_path, 'config', 'settings.json')

    # Load configuration
    configuration = config.load_config(config_path, keyfile_path=None)
    hostname = configuration['hostname']
    port = int(configuration['port'])
    username = configuration['username']
    password = configuration['password']
    ca_certs = '/etc/ssl/certs/ca-certificates.crt'

    signal.signal(signal.SIGINT, signal_handler)

    logger.info('Starting client...')
    loop = asyncio.get_event_loop()
    mqttc = MockIlluminator(
        loop, hostname, port,
        username=username, password=password, ca_certs=ca_certs,
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
    logger.info('Finished!')
