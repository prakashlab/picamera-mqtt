#!/usr/bin/env python3
"""Make the NeoPixel strip gently fade between white and dark."""

from intervention_system.illumination import illumination as il


def main():
    lights = il.Illumination(led_brightness=16)
    lights.color(il.color(255, 0, 0))


# Main program logic follows:
if __name__ == '__main__':
    main()
