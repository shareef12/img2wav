#!/usr/bin/env python3

"""Convert images to a wav file to display in a spectrogram.

If multiple images are specified, combine them into a single wav file.
"""

import argparse
import struct
import time
import wave

import numpy as np
from PIL import Image

HOLD_MULTIPLIER = 10240


def timeit(func):
    """Decorator to time a function's execution time. Used for benchmarking."""
    def timer(*args, **kwargs):
        before = time.time()
        ret = func(*args, **kwargs)
        print("{}: {}".format(func.__name__, time.time() - before))
        return ret
    return timer


def signal(outfile, frequency=5000, amplitude=5000, framerate=44100, duration=5):
    """Debugging function to generate a wav file with a single frequency signal."""
    wav = wave.open(outfile, "wb")
    wav.setparams((1, 2, framerate, 0, "NONE", "not compressed"))

    for i in range(0, framerate * duration):
        value = amplitude * np.sin(2 * np.pi * frequency * i / framerate)
        wav.writeframes(struct.pack("<h", value))
    wav.close()


def get_rows(image):
    """Get a list of rows of pixeldata.

    :param image: PIL.Image
    :return: A list of rows where each row is a list of pixel values
    :rtype: np.ndarray
    """

    # Convert to an 8-bit grayscale bmp
    img = Image.open(image).convert("L")

    # Build a numpy multidimensional array with the raw pixel data
    pixels = np.array(img.getdata())
    w, h = img.size
    return np.array([np.array(pixels[i:i+w]) for i in range(0, w*h, w)])


def normalize(frames):
    """Normalize frames to 16-bit signed values."""
    max_frame = max(frames)
    scalar = 0x7ff / max_frame
    return [int(scalar * val) for val in frames]


def convert_image(rows, frequency=2750, bandwidth=4000, framerate=11025):
    """Convert an image into audio sampling frames.

    :param rows: A list of pixeldata for each row. Each row is a list of pixel values.
    :param framerate: Output sampling frequency
    :param frequency: Output frequency around which to center the image
    :param bandwidth: Desired bandwidth for the image
    :return: A list of frames
    """

    # Get the number of milliseconds to hold each row. We want to expand images
    # to the same width, so narrow images should have a longer hold to maintain
    # a correct aspect ratio.
    height, width = rows.shape
    hold = HOLD_MULTIPLIER // width

    # Center the image around the specified frequency
    base_freq = frequency - int(bandwidth / 2)
    frames_per_row = framerate * hold // 1000

    # Generate an array of frequencies to manipulate and do some pre-processing
    # for optimization.
    freqs = np.linspace(base_freq, base_freq + bandwidth, width)
    freqs *= 2 * np.pi / framerate

    # Generate a matrix of signals for each row of the image
    frames = []
    for i, row in enumerate(rows):
        start = i * frames_per_row
        frame_nos = np.arange(start, start + frames_per_row)
        signals = np.array([np.cos(freqs[i] * frame_nos) for i in range(width)])
        signals = signals.T

        # Multiply the signals by the row value squared (amplitude)
        signals *= row ** 2
        frames.extend(np.sum(group) for group in signals)

    return frames


def img2wav(images, output, delay, frequency, bandwidth, samplerate):
    """Convert images to a wav file.

    :param images: List of image filenames to process
    :param output: Output filename
    :param delay: Number of milliseconds between image output
    :param frequency: Center frequency for audio output signal
    :param bandwidth: Bandwidth for audio output signal
    :param samplerate: Sample rate for audio output signal
    """

    print("[*] Writing wav file: {:s}".format(output))
    print("[*]   Center frequency: {:d}hz".format(frequency))
    print("[*]   Bandwidth       : {:d}hz".format(bandwidth))
    print("[*]   Sample rate     : {:d}hz".format(samplerate))
    print("[*]   Delay           : {:d}ms".format(delay))

    wavfile = wave.open(output, "wb")
    wavfile.setparams((1, 2, samplerate, 0, "NONE", "not compressed"))

    frames_per_delay = samplerate * delay // 1000
    delay_frames = b"\x00" * 2 * frames_per_delay

    for i, image in enumerate(images):
        print("[*] Processing: {:s}".format(image))
        # Convert image to raw time domain samples
        rows = get_rows(image)
        frames = convert_image(rows,
                               frequency=frequency,
                               bandwidth=bandwidth,
                               framerate=samplerate)

        # Normalize frames to 16-bit signed ints and emit them
        frames = normalize(frames)
        raw_frames = b"".join(struct.pack("<h", val) for val in frames)
        wavfile.writeframes(raw_frames)

        # If more images follow, add a gap of DELAY milliseconds
        if i < len(images) - 1:
            wavfile.writeframes(delay_frames)

    print("[+] Done")
    wavfile.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("images", nargs="+", type=str,
                        help="8-bit bmp images to process")
    parser.add_argument("-o", "--output", type=str, default="img.wav",
                        help="Output file to write the wav to (default: img.wav)")
    parser.add_argument("-d", "--delay", type=int, default=2000,
                        help="Delay in ms between images when more than one is specified (default: 2000)")
    parser.add_argument("-f", "--frequency", type=int, default=2750,
                        help="Center frequency for audio output signal (default: 2750)")
    parser.add_argument("-b", "--bandwidth", type=int, default=4000,
                        help="Bandwidth for audio output signal (default 4000)")
    parser.add_argument("-s", "--samplerate", type=int, default=11025,
                        help="Sample rate for audio output signal (default 11025)")

    args = parser.parse_args()

    img2wav(args.images, args.output, args.delay, args.frequency,
            args.bandwidth, args.samplerate)


if __name__ == "__main__":
    main()
