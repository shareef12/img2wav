# img2wav

img2wav is a simple command line utility to convert image files into audio clips
suitable for display in a spectrogram. Multiple images can be specified to
create a scrolling display.

It's relatively easy to tune parameters for waveform generation, allowing you to
optionally specify the delay between images, center frequency, image bandwidth,
and output file samplerate.

```
$ img2wav -o res/hackers.wav res/images/*
[*] Writing wav file: res/hackers.wav
[*]   Center frequency: 2750hz
[*]   Bandwidth       : 4000hz
[*]   Sample rate     : 11025hz
[*]   Delay           : 2000ms
[*] Processing: res/images/glider.png
[*] Processing: res/images/hackers.bmp
[*] Processing: res/images/hacktheplanet2.bmp
[*] Processing: res/images/hacktheplanet.jpg
[+] Done
```

![Spectrogram output example](res/hackers.gif)
