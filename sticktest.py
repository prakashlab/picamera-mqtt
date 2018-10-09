#!/usr/bin/env python3
"""Showcase various animation patterns on a NeoPixel strip."""

import signal
import argparse

import rpi_ws281x as ws

import illumination as il

def signal_handler(signum, frame):
    raise KeyboardInterrupt

# Main program logic follows:
if __name__ == '__main__':
    signal.signal(signal.SIGINT, signal_handler)

    lights = il.Illumination()

    print('Press Ctrl-C to quit.')

    try:
        while True:
            print('Color wipe animations.')
            for i in range(5):
                lights.color_wipe(ws.Color(255, 0, 0))  # Red wipe
                lights.color_wipe(ws.Color(0, 255, 0))  # Blue wipe
                lights.color_wipe(ws.Color(0, 0, 255))  # Green wipe
            print('Theater chase animations.')
            for i in range(5):
                lights.theater_chase(ws.Color(127, 127, 127))  # White theater chase
            for i in range(5):
                lights.theater_chase(ws.Color(127,   0,   0))  # Red theater chase
            for i in range(5):
                lights.theater_chase(ws.Color(  0,   0, 127))  # Blue theater chase
            print('Rainbow animations.')
            print('  Rainbow fade.')
            lights.rainbow()
            print('  Rainbow cycle.')
            for i in range(5):
                lights.rainbow_cycle()
            print('  Rainbow theater chase.')
            lights.theater_chase_rainbow()

    except KeyboardInterrupt:
        lights.clear()
