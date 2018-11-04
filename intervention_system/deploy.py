"""Utility functions and shared parameters for deployment."""

import asyncio
import logging
import os

from intervention_system import deploy_path

logger = logging.getLogger(__name__)

keys_path = deploy_path
settings_key_path = os.path.join(keys_path, 'settings.key')
# USB configs
client_configs_path = '/media/usb0/'
client_config_plain_name = 'settings.json'
client_config_cipher_name = 'settings_encrypted.json'
client_config_plain_path = os.path.join(
    client_configs_path, client_config_plain_name
)
# Sample configs
client_config_cipher_path = os.path.join(
    client_configs_path, client_config_cipher_name
)
client_configs_sample_path = os.path.join(deploy_path, 'config')
client_config_sample_cloudmqtt_name = 'settings_cloudmqtt.json'
client_config_sample_cloudmqtt_path = os.path.join(
    client_configs_sample_path, client_config_sample_cloudmqtt_name
)

service_name = 'mqtt_illumination'


async def reboot():
    """Trigger a system reboot."""
    logger.info('Rebooting system...')
    await asyncio.create_subprocess_exec(
        'systemctl', 'reboot',
        stdout=asyncio.subprocess.PIPE
    )

async def shutdown():
    """Trigger a system shutdown."""
    logger.info('Shutting down system...')
    await asyncio.create_subprocess_exec(
        'systemctl', 'poweroff',
        stdout=asyncio.subprocess.PIPE
    )

async def restart():
    """Trigger a service restart."""
    logger.info('Restarting service...')
    await asyncio.create_subprocess_exec(
        'systemctl', 'restart', service_name,
        stdout=asyncio.subprocess.PIPE
    )

async def git_pull(pi_username, restart_afterwards=False):
    """Trigger a repository update."""
    logger.info('Updating local repo...')
    process = await asyncio.create_subprocess_exec(
            'sudo', '-u', pi_username, 'git', 'pull',
            stdout=asyncio.subprocess.PIPE
        )
    await process.communicate()
    if restart_afterwards:
        await restart()
