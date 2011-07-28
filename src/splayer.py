#!/usr/bin/env python

# splayer - static audio player
#
# Copyright 2011 Jochen Skulj, jochen@jochenskulj.de
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

import os
import os.path
import sys
import threading
import time

from pygame import mixer

class MediaFile(object):
    """
    class for a media file
    """

    def __init__(self, filename, directory=None):
        """
        creates an instance
        Parameters:
        - filename
        - directory
        """
        self._playing = False
        if os.path.isfile(filename):
            self._directory = os.path.dirname(filename)
            self._filename = os.path.basename(filename)
        else:
            self._filename = filename
            if directory == None:
                self._directory = os.getcwd()
            else:
                self._directory = directory
        self._path = os.path.join(self._directory, self._filename)

    def exists(self):
        """
        checks if the file exists
        Returns:
        - True:  file exists
        - False: file doesn't exists
        """
        return os.path.isfile(self._path)

    def is_playing(self):
        """
        checks if the file is currently played
        Returns:
        - True:  file is played
        - False: file is not played
        """
        return self._playing

    def play(self):
        """
        plays the file
        """
        if not self.is_playing():
            if self.exists():
                mixer.init()
                print self._path
                mixer.music.load(self._path)
                print "play"
                mixer.music.play()
                # invoke play() for the second time to support
                # playing MP3
                mixer.music.play()
                self._playing = True
                last_position = mixer.music.get_pos()
                time.sleep(2)
                position = mixer.music.get_pos()
                while self.is_playing() and last_position < position:
                    time.sleep(2)
                    if self.is_playing():  
                        last_position = position
                        position = mixer.music.get_pos()
                        print position

def main(argv):
    """
    main function
    """
    l = len(argv)
    if l < 2:
        print "parameters missing."
    else:
        for i in range(1, l):
            filename = argv[i]
            mfile = MediaFile(filename)
            if not mfile.exists():
                print "file %s does not exists." % filename
            else:
                mfile.play()

if __name__ == "__main__":
    main(sys.argv)

