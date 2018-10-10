#!/usr/bin/env python3
"""Make the NeoPixel strip gently fade between white and dark."""

import asyncio
import contextlib
import signal

import illumination as il

import rpi_ws281x as ws


def signal_handler(signum, frame):
    """Catch any interrupt signal and raise a KeyboardInterrupt.

    Useful for translating SIGINTs sent from other processes into a KeyboardInterrupt.
    """
    raise KeyboardInterrupt


async def main():
    lights = il.Illumination(led_brightness=16)

    print('Press Ctrl-C to quit.')

    try:
        while True:
            await lights.breathe(255)
    except asyncio.CancelledError:
        lights.clear()


# Main program logic follows:
if __name__ == '__main__':
    signal.signal(signal.SIGINT, signal_handler)

    loop = asyncio.get_event_loop()
    task = loop.create_task(main())
    try:
        loop.run_until_complete(task)
    except KeyboardInterrupt:
        task.cancel()
        with contextlib.suppress(asyncio.CancelledError):
            loop.run_until_complete(task)
    finally:
        loop.close()
