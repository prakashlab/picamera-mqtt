#!/usr/bin/env python3
"""Make the NeoPixel strip gently fade between white and dark."""

import asyncio

from intervention_system.illumination import illumination as il
from intervention_system.util.async import (
    register_keyboard_interrupt_signals, run_function
)


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
    register_keyboard_interrupt_signals()
    run_function(main, cancel_pending_on_interrupt=False)
