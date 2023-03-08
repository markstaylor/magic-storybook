# magic-storybook
Raspberry Pi/RC522-based children's story reader

This is the code that runs the [Magic Storybook](https://markstaylor.uk/blog/2023/03/building-a-childrens-storybook-reader), a Tonies/Yoto-style story reader I built for my son.

It requires [my fork of the MFRC522-python library](https://github.com/markstaylor/MFRC522-python) and uses [python-vlc](https://pypi.org/project/python-vlc/) for playback.

The script looks for text on the NFC tag in the format `<s>filename</s>`, and then plays the file named `filename` in the specified path (by default, `/home/pi/stories/`). If the specified file is a directory, it will choose a random file from that directory to play.

If the tag is removed, playback will pause. Replacing the tag within a short interval will resume playback; after this interval, replacing the tag will start playback again from the beginning.
