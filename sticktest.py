#!/usr/bin/env python3
"""Showcase various animation patterns on a NeoPixel strip."""

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
    signal.signal(signal.SIGINT, signal_handler)

    lights = il.Illumination()

    print('Press Ctrl-C to quit.')

    try:
        while True:
            print('Color wipe animations.')
            for i in range(5):
                await lights.color_wipe(ws.Color(255, 0, 0))  # Red wipe
                await lights.color_wipe(ws.Color(0, 255, 0))  # Blue wipe
                await lights.color_wipe(ws.Color(0, 0, 255))  # Green wipe
            print('Theater chase animations.')
            for i in range(5):
                await lights.theater_chase(ws.Color(127, 127, 127))  # White theater chase
            for i in range(5):
                await lights.theater_chase(ws.Color(127, 0, 0))  # Red theater chase
            for i in range(5):
                await lights.theater_chase(ws.Color(0, 0, 127))  # Blue theater chase
            print('Rainbow animations.')
            print('  Rainbow fade.')
            await lights.rainbow()
            print('  Rainbow cycle.')
            for i in range(5):
                await lights.rainbow_cycle()
            print('  Rainbow theater chase.')
            await lights.theater_chase_rainbow()
    except asyncio.CancelledError:
        await lights.clear()


# Main program logic follows:
if __name__ == '__main__':
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
