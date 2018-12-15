"""Utility functions and shared parameters for deployment."""

import asyncio
import logging
import os

from picamera_mqtt import deploy_path

logger = logging.getLogger(__name__)

# Configs
client_configs_path = os.path.join(deploy_path, 'config')
client_config_plain_name = 'settings.json'
client_config_plain_path = os.path.join(
    client_configs_path, client_config_plain_name
)
# Sample configs
client_configs_sample_path = client_configs_path
client_config_sample_cloudmqtt_name = 'settings_cloudmqtt.json'
client_config_sample_cloudmqtt_path = os.path.join(
    client_configs_sample_path, client_config_sample_cloudmqtt_name
)
client_config_sample_localhost_name = 'settings_localhost.json'
client_config_sample_localhost_path = os.path.join(
    client_configs_sample_path, client_config_sample_localhost_name
)

service_name = 'mqtt_imaging'


async def daemon_reload():
    """Trigger a system daemon unit reload."""
    process = await asyncio.create_subprocess_exec(
        'systemctl', 'daemon-reload',
        stdout=asyncio.subprocess.PIPE
    )
    await process.communicate()


async def reconnect():
    """Trigger a system dhcpcd restart."""
    logger.info('Restarting dhcpcd systemctl service...')
    await daemon_reload()
    process = await asyncio.create_subprocess_exec(
        'systemctl', 'restart', 'dhcpcd',
        stdout=asyncio.subprocess.PIPE
    )
    await process.communicate()


async def reboot():
    """Trigger a system reboot."""
    logger.info('Rebooting system...')
    await asyncio.create_subprocess_exec(
        'systemctl', 'reboot',
        stdout=asyncio.subprocess.PIPE
    )
    raise KeyboardInterrupt


async def shutdown():
    """Trigger a system shutdown."""
    logger.info('Shutting down system...')
    await asyncio.create_subprocess_exec(
        'systemctl', 'poweroff',
        stdout=asyncio.subprocess.PIPE
    )
    raise KeyboardInterrupt


async def restart():
    """Trigger a service restart."""
    logger.info('Restarting service...')
    await daemon_reload()
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
