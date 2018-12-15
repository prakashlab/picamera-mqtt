#!/usr/bin/env python3
"""Camera abstraction layer."""

import base64
import datetime
import time
from io import BytesIO

from PIL import Image


class Camera(object):
    def __init__(
        self, pi_camera, iso=60, exposure_mode='off', shutter_speed=20000,
        awb_mode='off', awb_gains=(2, 1)
    ):
        self.pi_camera = pi_camera
        time.sleep(2)
        pi_camera.iso = iso
        pi_camera.exposure_mode = exposure_mode
        pi_camera.shutter_speed = shutter_speed
        pi_camera.awb_mode = awb_mode
        pi_camera.awb_gains = awb_gains
        self.zoom = 1
        self.nominal_shutter_speed = shutter_speed / 1000.0

    def set_roi(self, zoom):
        self.zoom = zoom
        x_start = 0.5 - 1 / (2 * zoom)
        y_start = x_start
        width = 1 / zoom
        height = width
        self.pi_camera.zoom = (x_start, y_start, width, height)

    def set_shutter_speed(self, shutter_speed):
        self.nominal_shutter_speed = shutter_speed
        speed_int = int(shutter_speed * 1000)
        # current_framerate = self.pi_camera.framerate
        new_framerate = int(1000000 / float(speed_int))
        self.pi_camera.framerate = min(new_framerate, 30)
        self.pi_camera.shutter_speed = speed_int

    def capture_file(self, filename_prefix, **format_args):
        timestamp = '{:%Y-%m-%d_%H-%M-%S-%f}'.format(
            datetime.datetime.now()
        )[:-3]
        filename = '{}_{}.jpg'.format(filename_prefix, timestamp)
        print('Saving capture to:', filename)
        self.pi_camera.capture(filename, **format_args)

    def capture_buffer(self, format='jpeg', **format_args):
        stream = BytesIO()
        self.pi_camera.capture(stream, format=format, **format_args)
        stream.seek(0)
        return stream

    def capture_pil(self, format='jpeg', **format_args):
        return Image.open(self.capture_buffer(format=format, **format_args))

    def get_params(self):
        return {
            'sensor_mode': self.pi_camera.sensor_mode,
            'zoom': self.zoom,
            'roi': {
                'x': self.pi_camera.zoom[0],
                'y': self.pi_camera.zoom[1],
                'w': self.pi_camera.zoom[2],
                'h': self.pi_camera.zoom[3],
            },
            'iso': self.pi_camera.iso,
            'exposure_mode': self.pi_camera.exposure_mode,
            'shutter_speed': {
                'nominal': self.nominal_shutter_speed,
                'actual': self.pi_camera.shutter_speed
            },
            'awb_mode': self.pi_camera.awb_mode,
            'awb_gains': {
                'red': {
                    'numerator': self.pi_camera.awb_gains[0].numerator,
                    'denominator': self.pi_camera.awb_gains[0].denominator
                },
                'blue': {
                    'numerator': self.pi_camera.awb_gains[1].numerator,
                    'denominator': self.pi_camera.awb_gains[1].denominator
                }
            },
            'resolution': {
                'width': self.pi_camera.resolution[0],
                'height': self.pi_camera.resolution[1]
            },
            'analog_gain': {
                'numerator': self.pi_camera.analog_gain.numerator,
                'denominator': self.pi_camera.analog_gain.denominator
            },
            'digital_gain': {
                'numerator': self.pi_camera.digital_gain.numerator,
                'denominator': self.pi_camera.digital_gain.denominator
            },
            'exposure_compensation': self.pi_camera.exposure_compensation,
            'brightness': self.pi_camera.brightness,
            'contrast': self.pi_camera.contrast,
            'saturation': self.pi_camera.saturation,
            'sharpness': self.pi_camera.sharpness,
            'hflip': self.pi_camera.hflip,
            'vflip': self.pi_camera.vflip,
            'rotation': self.pi_camera.rotation,
            'image_denoise': self.pi_camera.image_denoise,
            'revision': self.pi_camera.revision
        }


class MockCamera(object):
    def capture_pil(self, format='jpeg', **format_args):
        import numpy as np
        image_array = np.random.randint(
            0, 256, dtype=np.uint8, size=(1080, 1920, 3)
        )
        return Image.fromarray(image_array)

    def get_params(self):
        return {
            'mock': 'white noise'
        }


def buffer_to_base64(image_buffer, encoding='utf-8'):
    return base64.b64encode(image_buffer.getvalue()).decode(encoding)


def pil_to_base64(image_pil, encoding='utf-8', format='jpeg', **format_args):
    image_buffer = BytesIO()
    image_pil.save(image_buffer, format=format, **format_args)
    return buffer_to_base64(image_buffer, encoding=encoding)


def base64_to_pil(image_base64):
    return Image.open(BytesIO(base64.b64decode(image_base64)))
