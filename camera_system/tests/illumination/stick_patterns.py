#!/usr/bin/env python3
"""Showcase various animation patterns on a NeoPixel strip."""

import asyncio

from intervention_system.illumination import illumination as il
from intervention_system.util.async import (
    register_keyboard_interrupt_signals, run_function
)


async def main():
    lights = il.Illumination()

    print('Press Ctrl-C to quit.')

    try:
        while True:
            print('Breathe animation.')
            for i in range(5):
                await lights.breathe(255)
            print('Color wipe animations.')
            for i in range(5):
                await lights.color_wipe(il.color(255, 0, 0))  # Red wipe
                await lights.color_wipe(il.color(0, 255, 0))  # Blue wipe
                await lights.color_wipe(il.color(0, 0, 255))  # Green wipe
            print('Theater chase animations.')
            for i in range(5):
                await lights.theater_chase(il.color(127, 127, 127))  # White theater chase
            for i in range(5):
                await lights.theater_chase(il.color(127, 0, 0))  # Red theater chase
            for i in range(5):
                await lights.theater_chase(il.color(0, 0, 127))  # Blue theater chase
            print('Rainbow animations.')
            print('  Rainbow fade.')
            await lights.rainbow()
            print('  Rainbow cycle.')
            for i in range(5):
                await lights.rainbow_cycle()
            print('  Rainbow theater chase.')
            await lights.theater_chase_rainbow()
    except asyncio.CancelledError:
        lights.clear()


# Main program logic follows:
if __name__ == '__main__':
    register_keyboard_interrupt_signals()
    run_function(main, cancel_pending_on_interrupt=False)
