#!/usr/bin/env python2

"""Convert 8-bit bmp to wav to display in a spectrogram."""

from __future__ import print_function
import argparse
import math
import os
import struct
import wave
from PIL import Image

def get_rows(image):
	"""Get a list of rows of pixeldata.

	:param image: PIL.Image
	:returns: A list of rows where each row is a list of pixel values
	"""
	pixels = list(image.getdata())
	width, height = image.size

	rows = []
	for i in xrange(height):
		start = i * width
		rows.append(pixels[start:start+width])
	
	return rows


def normalize(frames):
	max_f = max(frames)
	mult = 0x7fe / max_f
	return [mult * val for val in frames]


def write_wav(outfile, rows, framerate=11025, frequency=3000, bandwidth=2000, hold=50):
	
	wav = wave.open(outfile, "wb")
	wav.setparams((1, 2, framerate, 0, "NONE", "not compressed"))

	base_freq = frequency - int(bandwidth / 2)
	frames_per_hold = framerate * hold / 1000

	#print(frames_per_hold)
	#print(len(rows) * frames_per_hold)
	values = []
	for i in xrange(0, len(rows)):
		for j in xrange(0, frames_per_hold):
			frame = i * frames_per_hold + j
			w = 2 * math.pi * frame / framerate
			
			value = 0
			for col, val in enumerate(rows[i]):
				freq = base_freq + bandwidth * col / len(rows)
				amp = val * 5
				
				value += amp * math.cos(w * freq)
			
			values.append(value)
	
	norm = normalize(values)
	wav.writeframes("".join(struct.pack("<h", int(val)) for val in norm))

	wav.close()

def signal(outfile, frequency=5000, amplitude=5000, framerate=44100, duration=5):
	wav = wave.open(outfile, "wb")
	wav.setparams((1, 2, framerate, 0, "NONE", "not compressed"))
	
	for i in xrange(0, framerate * duration):
		value = amplitude * math.sin(2 * math.pi * frequency * i / 44100)
		wav.writeframes(struct.pack("<h", value))
	wav.close()

def main(infile, outfile):
	im = Image.open(infile)
	rows = get_rows(im)

	write_wav(outfile, rows)


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