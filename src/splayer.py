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

import gtk
import gtk.gdk
import gtk.glade
import os
import os.path
import sys
import threading
import time

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
        self._status_path = self.get_status_path(self._filename, self._directory)

    def get_status_path(self, filename, directory):
        """
        returns the path of the status file
        Parameters:
        - filename
          filename of the media file
        - directory
          directory of the media file
        Returns:
        - path of the status file
        """
        status_filename = ".%s.splayer" % filename
        return os.path.join(directory, status_filename)

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
        pass

    def get_status(self):
        """
        Returns:
        - current position from the status file
        """
        return 16.0

    def update_status(self, duration):
        pass

    def remove_status(self):
        pass

class PlayerWindow(object):

    def __init__(self):
        """
        creates an instance
        """
        self._widget_tree = self.init_widget_tree()
 
    def init_widget_tree(self):
        """
        initializes the widget tree
        Returns:
        - created widget tree
        """
        gladefile = "splayer.glade"
        windowname = "playerwindow"
        widget_tree = gtk.glade.XML(gladefile, windowname)
        dic = {"on_playerwindow_destroy" : self.on_quit
        , "on_quit" : self.on_quit }
        # , "on_add_directory" : self.on_add_directory
        # , "on_remove_directory" : self.on_remove_directory
        # , "on_synchronize" : self.on_synchronize
        # , "on_exit" : self.on_exit }
        widget_tree.signal_autoconnect(dic)
        return widget_tree

    def set_filename(self, filename):
        """
        sets the filename
        Parameters:
        - filename
          filename to set
        """
        widget = self._widget_tree.get_widget("label_filename")
        widget.set_text(filename)
        print filename

    def on_open(self, widget):
        """
        handles the event to open a file
        Parameters:
        - widget
          widget that triggered the event
        """
        print "on_open()"

    def on_play_stop(self, widget):
        """
        handles the event to play or stop the media file
        Parameters:
        - widget
          widget that triggered the event
        """
        print "on_play_stop()"

    def on_reset(self, widget):
        """
        handles the event to reset the playing position
        Parameters:
        - widget
          widget that triggered the event
        """
        print "on_reset()"

    def on_quit(self, widget):
        """
        handles the event to quit the application
        Parameters:
        - widget
          widget that triggered the event
        """
        print "on_quit()"


if __name__ == "__main__":
    # gtk.gdk.threads_init()
    window = PlayerWindow()
    if len(sys.argv) > 1:
        window.set_filename(sys.argv[1])
    gtk.main()
