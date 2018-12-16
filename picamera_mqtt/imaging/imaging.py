#!/usr/bin/env python3
"""Camera abstraction layer."""

import base64
import datetime
import time
from io import BytesIO

from PIL import Image


class BaseCamera(object):
    def set_roi(self, zoom=None):
        pass

    def set_shutter_speed(self, shutter_speed=None):
        pass

    def set_iso(self, iso=None):
        pass

    def set_resolution(self, width=None, height=None):
        pass

    def set_awb_gains(self, red=None, blue=None):
        pass

    def set_params(
        self, roi_zoom=None, shutter_speed=None, iso=None,
        resolution_width=None, resolution_height=None,
        awb_gain_red=None, awb_gain_blue=None
    ):
        self.set_roi(zoom=roi_zoom)
        self.set_shutter_speed(shutter_speed=shutter_speed)
        self.set_iso(iso=iso)
        self.set_resolution(width=resolution_width, height=resolution_height)
        self.set_awb_gains(red=awb_gain_red, blue=awb_gain_blue)

    def capture_pil(self, format='jpeg', **format_args):
        pass

    def get_params(self):
        return {}


class Camera(BaseCamera):
    def __init__(
        self, pi_camera, iso=60, exposure_mode='off', shutter_speed=20000,
        awb_mode='off', awb_gains=(2, 1)
    ):
        super().__init__()
        self.pi_camera = pi_camera
        time.sleep(2)
        pi_camera.iso = iso
        pi_camera.exposure_mode = exposure_mode
        pi_camera.shutter_speed = shutter_speed
        pi_camera.awb_mode = awb_mode
        pi_camera.awb_gains = awb_gains
        self.zoom = 1
        self.nominal_shutter_speed = shutter_speed / 1000.0

    def set_roi(self, zoom=None):
        if zoom is None:
            return
        self.zoom = zoom
        x_start = 0.5 - 1 / (2 * zoom)
        y_start = x_start
        width = 1 / zoom
        height = width
        self.pi_camera.zoom = (x_start, y_start, width, height)

    def set_shutter_speed(self, shutter_speed=None):
        if shutter_speed is None:
            return
        self.nominal_shutter_speed = shutter_speed
        speed_int = int(shutter_speed * 1000)
        # current_framerate = self.pi_camera.framerate
        new_framerate = int(1000000 / float(speed_int))
        self.pi_camera.framerate = min(new_framerate, 30)
        self.pi_camera.shutter_speed = speed_int

    def set_iso(self, iso=None):
        if iso is None:
            return
        self.pi_camera.iso = iso

    def set_resolution(self, width=None, height=None):
        if width is None or height is None:
            return
        self.pi_camera.resolution = (width, height)

    def set_awb_gains(self, red=None, blue=None):
        if red is None and blue is None:
            return
        if red is None:
            red = self.pi_camera.awb_gains[0]
        if blue is None:
            blue = self.pi_camera.awb_gains[1]
        self.pi_camera.awb_gains = (red, blue)

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


class MockCamera(BaseCamera):
    def __init__(self, *args, **kwargs):
        super().__init__()
        self.zoom = None
        self.shutter_speed = None
        self.iso = None
        self.resolution = (1920, 1080)
        self.awb_gains = (None, None)

    def set_roi(self, zoom):
        if zoom is None:
            return
        self.zoom = zoom

    def set_shutter_speed(self, shutter_speed):
        if shutter_speed is None:
            return
        self.shutter_speed = shutter_speed

    def set_iso(self, iso=None):
        if iso is None:
            return
        self.iso = iso

    def set_resolution(self, width=None, height=None):
        if width is None or height is None:
            return
        self.resolution = (width, height)

    def set_awb_gains(self, red=None, blue=None):
        if red is None and blue is None:
            return
        if red is None:
            red = self.awb_gains[0]
        if blue is None:
            blue = self.awb_gains[1]
        self.awb_gains = (red, blue)

    def capture_pil(self, format='jpeg', **format_args):
        import numpy as np
        image_array = np.random.randint(
            0, 256, dtype=np.uint8,
            size=(self.resolution[1], self.resolution[0], 3)
        )
        return Image.fromarray(image_array)

    def get_params(self):
        return {
            'sensor_mode': 'mock white noise',
            'zoom': self.zoom,
            'shutter_speed': self.shutter_speed,
            'iso': self.iso,
            'resolution': {
                'width': self.resolution[0],
                'height': self.resolution[1]
            },
            'awb_gains': {
                'red': self.awb_gains[0],
                'blue': self.awb_gains[1]
            }
        }


# Image representation conversion

def buffer_to_base64(image_buffer, encoding='utf-8'):
    return base64.b64encode(image_buffer.getvalue()).decode(encoding)


def pil_to_base64(image_pil, encoding='utf-8', format='jpeg', **format_args):
    image_buffer = BytesIO()
    image_pil.save(image_buffer, format=format, **format_args)
    return buffer_to_base64(image_buffer, encoding=encoding)


def base64_to_pil(image_base64):
    return Image.open(BytesIO(base64.b64decode(image_base64)))


# Command-line args

def add_camera_params_arguments(arg_parser):
    arg_parser.add_argument(
        '--roi_zoom', '-z', type=float, default=None,
        help='ROI zoom factor. If unspecified, don\'t change the setting.'
    )
    arg_parser.add_argument(
        '--shutter_speed', '-s', type=float, default=None,
        help='Shutter speed in ms. If unspecified, don\'t change the setting.'
    )
    arg_parser.add_argument(
        '--iso', '-i', type=int, default=None,
        help='ISO. If unspecified, don\'t change the setting.'
    )
    arg_parser.add_argument(
        '--resolution_width', '-x', type=int, default=None,
        help=(
            'Imaging resolution width. If unspecified, don\'t change the '
            'setting. Both width and height must be specified to change resolution.'
        )
    )
    arg_parser.add_argument(
        '--resolution_height', '-y', type=int, default=None,
        help=(
            'Imaging resolution height. If unspecified, don\'t change the '
            'setting. Both width and height must be specified to change resolution.'
        )
    )
    arg_parser.add_argument(
        '--awb_gain_red', '-r', type=float, default=None,
        help='AWB gain for red. If unspecified, don\'t change the setting.'
    )
    arg_parser.add_argument(
        '--awb_gain_blue', '-b', type=float, default=None,
        help='AWB gain for blue. If unspecified, don\'t change the setting.'
    )

def parse_camera_params_from_args(parsed_args):
    full_params = {
        'roi_zoom': parsed_args.roi_zoom,
        'shutter_speed': parsed_args.shutter_speed,
        'iso': parsed_args.iso,
        'resolution_width': parsed_args.resolution_width,
        'resolution_height': parsed_args.resolution_height,
        'awb_gain_red': parsed_args.awb_gain_red,
        'awb_gain_blue': parsed_args.awb_gain_blue
    }
    return {
        param: value
        for (param, value) in full_params.items()
        if value is not None
    }
