#!/usr/bin/env python3
"""Adapted from the Arduino NeoPixel library strandtest example."""

import asyncio


def rescale(value, in_min, in_max, out_min, out_max):
    """Rescale a value from an input range to an output range."""
    return (
        (value - in_min) * (out_max - out_min)
        / (in_max - in_min) + out_min
    )

def clamp(value, range_min, range_max):
    """Clamp a value within a range."""
    return min(max(value, range_min), range_max)

def color(red, green, blue):
    """Return a ws281x color."""
    return (red << 16) | (green << 8) | blue

def wheel(pos):
    """Generate rainbow colors across 0-255 positions."""
    if pos < 85:
        return color(pos * 3, 255 - pos * 3, 0)
    elif pos < 170:
        pos -= 85
        return color(255 - pos * 3, 0, pos * 3)
    else:
        pos -= 170
        return color(0, pos * 3, 255 - pos * 3)

async def sleep_ms(duration):
    """Sleep for the specified duration in milliseconds."""
    await asyncio.sleep(duration / 1000.0)


class Illumination:
    """Handles illumination animation for a NeoPixel device."""

    def __init__(
        self, num_leds=8, led_pin=18, led_brightness=255,
        led_freq=800000, led_dma=10, led_channel=0,
        led_invert=False,
    ):
        """
        Initialize a NeoPixel device.

        Arguments:
            num_leds: Number of LEDs on the device
            led_pin: GPIO pin connected to the pixels. 18 uses PWM,
                while 10 uses SPI /dev/spidev0.0
            led_brightness: Set to 0 for darkest and 255 for brightest.
            led_freq: LED signal frequency in Hz (usually 800 khz)
            led_dma: DMA channel to use for generating signal.
                Try 10, and avoid 5 (as 5 may brick a RPi 3!).
            led_channel: Set to 1 for GPIOs 13, 19, 41, 45, or 53
            led_invert: Whether to invert the signal. Useful when
                using an NPN transistor level shift.
        """
        import rpi_ws281x as ws
        strip = ws.Adafruit_NeoPixel(
            num_leds, led_pin, led_freq, led_dma,
            led_invert, led_brightness, led_channel
        )
        self.strip = strip
        try:
            self.strip.begin()
        except RuntimeError:
            raise RuntimeError(
                'Could not initiate control of the LED device. '
                'Make sure the program is run with privileged permissions!'
            )

    # Define functions which animate LEDs in various ways.
    def color(self, color):
        """Set color for entire display."""
        for i in range(self.strip.numPixels()):
            self.strip.setPixelColor(i, color)
        self.strip.show()

    async def breathe(self, intensity, wait_ms=2):
        """Gently fade in and out."""
        for j in range(intensity):
            for i in range(self.strip.numPixels()):
                self.strip.setPixelColor(i, color(j, j, j))
            self.strip.show()
            await sleep_ms(wait_ms)
        for j in range(intensity):
            for i in range(self.strip.numPixels()):
                self.strip.setPixelColor(i, color(intensity - j, intensity - j, intensity - j))
            self.strip.show()
            await sleep_ms(wait_ms)

    async def color_wipe(self, wipe_color, wait_ms=50):
        """Wipe color across display a pixel at a time."""
        for i in range(self.strip.numPixels()):
            self.strip.setPixelColor(i, wipe_color)
            self.strip.show()
            await sleep_ms(wait_ms)

    async def theater_chase(self, theater_color, wait_ms=50):
        """Movie theater light style chaser animation."""
        for q in range(3):
            for i in range(0, self.strip.numPixels(), 3):
                self.strip.setPixelColor(i+q, theater_color)
            self.strip.show()
            await sleep_ms(wait_ms)
            for i in range(0, self.strip.numPixels(), 3):
                self.strip.setPixelColor(i+q, 0)

    async def rainbow(self, wait_ms=20):
        """Draw rainbow that fades across all pixels at once."""
        for j in range(256):
            for i in range(self.strip.numPixels()):
                self.strip.setPixelColor(
                    i, wheel((i + j) & 255)
                )
            self.strip.show()
            await sleep_ms(wait_ms)

    async def rainbow_cycle(self, wait_ms=2):
        """Draw rainbow that uniformly distributes itself across all pixels."""
        for j in range(256):
            for i in range(self.strip.numPixels()):
                self.strip.setPixelColor(i, wheel(
                    (int(i * 256 / self.strip.numPixels()) + j) & 255
                ))
            self.strip.show()
            await sleep_ms(wait_ms)

    async def theater_chase_rainbow(self, wait_ms=20):
        """Rainbow movie theater light style chaser animation."""
        for j in range(256):
            for q in range(3):
                for i in range(0, self.strip.numPixels(), 3):
                    self.strip.setPixelColor(
                        i + q, wheel((i + j) % 255)
                    )
                self.strip.show()
                await sleep_ms(wait_ms)
                for i in range(0, self.strip.numPixels(), 3):
                    self.strip.setPixelColor(i + q, 0)

    def clear(self):
        """Turn off all LEDs."""
        clear_color = color(0, 0, 0)
        for i in range(self.strip.numPixels()):
            self.strip.setPixelColor(i, clear_color)
        self.strip.show()
