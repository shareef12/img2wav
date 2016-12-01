#!/usr/bin/env python2

"""Convert 8-bit bmp to wav to display in a spectrogram."""

from __future__ import print_function
import argparse
import math
import numpy as np
import os
import struct
import wave
from PIL import Image

def get_rows(image):
    """Get a list of rows of pixeldata.

    :param image: PIL.Image
    :returns: A list of rows where each row is a list of pixel values
    :rtype: list(np.array, np.array, np.array, ...)
    """

    pixels = np.array(image.getdata())
    width, height = image.size

    rows = []
    for i in xrange(height):
        start = i * width
        row = np.array(pixels[start:start+width])
        rows.append(row)

    return rows


def normalize(frames):
    max_frame = max(frames)
    scalar = 0x7ff / max_frame
    return [int(scalar * val) for val in frames]


def convert_image(rows, framerate=11025, frequency=3000, bandwidth=2000, hold=40):
    """Convert an image into audio sampling frames.

    :param rows: A list of pixeldata for each row. Each row is a list of pixel values.
    :param framerate: Output sampling frequency
    :param frequency: Output frequency around which to center the image
    :param bandwidth: Desired bandwidth for the image. This should be proportional to
        the hold param to balance width/heigh in the waterfall display.
    :param hold: Number of milliseconds to hold a specific signal for a row
    """

    # Center the image around the specified frequency
    base_freq = frequency - int(bandwidth / 2)
    frames_per_hold = framerate * hold / 1000

    # Generate an array of frequencies we'll be manipulating
    freqs = np.linspace(base_freq, base_freq+bandwidth, len(rows[0]))

    # Do some pre-processing for optimization
    freqs *= 2 * np.pi / framerate

    # Generate all frames
    frames = []
    for i, row in enumerate(rows):
        amps = row * 5
        for j in xrange(0, frames_per_hold):
            frame_no = i * frames_per_hold + j
            frame_val = np.sum(amps * np.cos(frame_no * freqs))
            frames.append(frame_val)
    
    return frames


def write_wav(outfile, frames, framerate=11025):
    # Normalize frames to 16-bit signed ints
    norm_frames = normalize(frames)
    raw_frames = "".join(struct.pack("<h", val) for val in norm_frames)

    # Write the wav file
    wav = wave.open(outfile, "wb")
    wav.setparams((1, 2, framerate, 0, "NONE", "not compressed"))
    wav.writeframes(raw_frames)
    wav.close()


def signal(outfile, frequency=5000, amplitude=5000, framerate=44100, duration=5):
    wav = wave.open(outfile, "wb")
    wav.setparams((1, 2, framerate, 0, "NONE", "not compressed"))
    
    for i in xrange(0, framerate * duration):
        value = amplitude * math.sin(2 * math.pi * frequency * i / framerate)
        wav.writeframes(struct.pack("<h", value))
    wav.close()

def main(infile, outfile):
    im = Image.open(infile)
    rows = get_rows(im)
    frames = convert_image(rows)
    write_wav(outfile, frames)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=str,
                        help="8-bit bmp image to process")
    parser.add_argument("-o", "--output", type=str,
                        help="Output file to write the wav to")
    args = parser.parse_args()

    if args.output is None:
        fname, _ = os.path.splitext(args.input)
        args.output = "{}.wav".format(fname)

    main(args.input, args.output)