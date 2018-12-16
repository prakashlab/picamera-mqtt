#!/usr/bin/env python3
"""Capture an image."""
import argparse
import json

from picamera_mqtt.imaging import imaging
from picamera_mqtt.util import files


def main(camera_params):
    camera = imaging.MockCamera()
    camera.set_params(**camera_params)
    print('Capturing image...')
    image_pil = camera.capture_pil(quality=100)
    print('Captured image!')
    print('Saving capture_mock_pil.jpg...')
    image_pil.save('capture_mock_pil.jpg', quality=100)
    print('Saved capture_mock_pil.jpg!')
    print('Converting to base64...')
    image_base64 = imaging.pil_to_base64(image_pil, quality=80)
    print('Converted to base64!')
    message = {'image': image_base64}
    print('Dumping to json...')
    message_json = json.dumps(message)
    print('Dumped to json!')
    print('Loading from json...')
    message = json.loads(message_json)
    print('Loaded from json!')
    image_base64_string = message['image']
    print('Saving capture_mock_final.jpg...')
    files.b64_string_bytes_save(
        image_base64_string, 'capture_mock_final.jpg'
    )
    print('Saved capture_mock_final.jpg!')
    print(camera.get_params())


# Main program logic follows:
if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Capture a mock image of random noise.'
    )
    imaging.add_camera_params_arguments(parser)
    args = parser.parse_args()
    camera_params = imaging.parse_camera_params_from_args(args)

    main(camera_params)
