#!/usr/bin/env python3
"""Make the NeoPixel strip gently fade between white and dark."""

import illumination as il

import rpi_ws281x as ws


def main():
    lights = il.Illumination(led_brightness=16)
    lights.color(ws.Color(255, 0, 0))


# Main program logic follows:
if __name__ == '__main__':
    main()
