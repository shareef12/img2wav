#!/usr/bin/env python2

"""Convert 8-bit bmp to wav to display in a spectrogram."""

from __future__ import print_function
import argparse
import glob
import os
import random
import struct
import time
import wave


def main(indir, outfile, delay, framerate=11025):
    
    params = (1, 2, framerate, 0, "NONE", "not compressed")
    out = wave.open(outfile, "wb")
    out.setparams((params))

    search = os.path.join(indir, "*.wav")
    for fname in glob.glob(search):
        if fname == outfile:
            continue

        print("[+] Converting: {}".format(fname))
        wav = wave.open(fname, "rb")
        if wav.getparams()[:3] != out.getparams()[:3]:
            raise IOError("Incompatible wav file {}: params {}".format(fname, wav.getparams()))

        nframes = wav.getnframes()
        out.writeframes(wav.readframes(nframes))
        print("[+] Converted")

        # Add random noise between frames
        nframes = framerate * delay / 1000
        frames = "".join(struct.pack("<h", random.randint(-4, 4)) for i in xrange(nframes))
        out.writeframes("\x00" * 2 * nframes)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=str,
                        help="Directory of wav files to combine")
    parser.add_argument("-o", "--output", type=str, default="combined.wav",
                        help="Output file to write the wav to")
    parser.add_argument("-d", "--delay", type=int, default=2000,
                        help="Delay in ms between wav file output")
    args = parser.parse_args()

    main(args.input, args.output, args.delay)