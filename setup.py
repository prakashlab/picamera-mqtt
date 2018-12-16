import setuptools

with open('README.md', 'r') as f:
    long_description = f.read()

setuptools.setup(
    name='picamera-mqtt',
    version='0.0.4',
    author='Ethan Li',
    author_email='lietk12@gmail.com',
    description=(
        'MQTT-based control and image capture with local and remote networked '
        'Raspberry Pi cameras.'
    ),
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/ethanjli/picamera-mqtt',
    packages=setuptools.find_packages(),
    license='BSD 3-Clause License',
    install_requires=[
        'paho-mqtt',
        'pillow'
    ],
    extras_require={
        'picamera_client': ['picamera'],
        'mock_camera_client': ['numpy']
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Development Status :: 3 - Alpha',
        'Topic :: Multimedia :: Graphics :: Capture :: Digital Camera'
    ]
)
