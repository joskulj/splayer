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
import gtk.glade
import gobject
import os
import os.path
import pygtk
import pygst
pygst.require("0.10")
import gst
import sys
import threading
import time

from threading import Thread

gtk.gdk.threads_init()

class MediaFile(object):
    """
    class for a media file
    """

    def __init__(self, filename):
        """
        creates an instance
        Parameters:
        - filename
          filename of the media file
        """
        self._player = None
        self._playing = False
        if filename != None:
            if os.path.isfile(filename):
                self._directory = os.path.dirname(filename)
                self._filename = os.path.basename(filename)
            else:
                self._filename = filename
                self._directory = os.getcwd()
            self._path = os.path.join(self._directory, self._filename)
            # self._status_path = self.get_status_path(self._filename, self._directory)
        else:
            self._filename = None
            self._directory = None
            self._path = None

    def get_filename(self):
        """
        Returns:
        - filename of the media file
        """
        return self._filename

    def get_uri(self):
        """
        Returns:
        - uri of the media file
        """
        return "file://" + self._path

    def get_path(self):
        """
        Returns:
        - path of the media file
        """
        return self._path

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
        result = False
        if self._path != None:
            result = os.path.isfile(self._path)
        return result
        self._playing = False

    def get_status(self):
        """
        Returns:
        - current position from the status file
        """
        result = 0
        if self._player != None:
            result = self._player.query_position(gst.FORMAT_TIME, None)[0]
        return result

    def update_status(self, duration):
        pass

    def remove_status(self):
        pass

class MediaPlayer(object):
    """
    class to play a media file
    """

    def __init__(self, mediafile):
        """
        creates an instance
        Parameters:
        - mediafile
          media file to play
        """
        self._mediafile = mediafile
        self._pipeline = None
        self._pipeline = gst.element_factory_make("playbin2", "player")
        fakesink = gst.element_factory_make("fakesink", "fakesink")
        self._pipeline.set_property("video-sink", fakesink)
        self._pipeline.set_property("uri", mediafile.get_uri())

    def play(self, startpos=None):
        """
        starts playing the media file
        Parameter
        - startpos (optional)
          position to start playing
        """
        if self._pipeline:
            self._pipeline.set_state(gst.STATE_PLAYING)
            if startpos:
                time.sleep(0.2)
                self._pipeline.seek_simple(gst.FORMAT_TIME, \
                    gst.SEEK_FLAG_FLUSH, startpos)

    def stop(self):
        """
        stops playing the media file
        """
        if self._pipeline:
            self._pipeline.set_state(gst.STATE_NULL)

    def get_duration(self):
        """
        Returns:
        - duration of the stream
        """
        result = -1
        if self._pipeline:
           result = self._pipeline.query_duration(gst.FORMAT_TIME, None)[0]
        return result

    def get_position(self):
        """
        Returns:
        - current position
        """
        result = -1
        if self._pipeline:
            result = self._pipeline.query_position(gst.FORMAT_TIME, None)[0]
        return result

class PlayerWindow(object):
    """
    GTK Window for the player
    """

    def __init__(self):
        """
        creates an instance
        """
        self._running = True
        self._media_file = MediaFile(None)
        self._widget_tree = self.init_widget_tree()
        self._player = None
        self.update_widgets()
        self._update_thread = Thread(target=self.update_state)
        self._update_thread.start()

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
        , "on_open" : self.on_open
        , "on_play_stop" : self.on_play_stop
        , "on_quit" : self.on_quit }
        widget_tree.signal_autoconnect(dic)
        return widget_tree

    def update_widgets(self):
        """
        updates the widgets of the window
        """
        play_button = self._widget_tree.get_widget("button_play_stop")
        label = self._widget_tree.get_widget("label_filename")
        if self._media_file.exists():
            play_button.set_sensitive(True)
            if self._player:
                play_button.set_label("_Stop")
            else:
                play_button.set_label("_Play")
            label.set_text(self._media_file.get_filename())
        else:
            play_button.set_sensitive(False)
            label.set_text("")

    def update_state(self):
        """
        updates the state
        """
        while self._running:
            if self._player:
                position = self._player.get_position()
                duration = self._player.get_duration()
                fraction = float(position) / float(duration)
                self.set_progress(fraction)
            time.sleep(1)
        print "update stop"

    def set_filename(self, filename):
        """
        sets the filename
        Parameters:
        - filename
          filename to set
        """
        self._media_file = MediaFile(filename)
        # TODO: stop and delete media player
        self.update_widgets()

    def set_progress(self, progress):
        """
        updates the progress bar
        Parameters:
        - progress
          value between 0.0 and 1.0
        """
        widget = self._widget_tree.get_widget("progressbar")
        widget.set_fraction(progress)

    def on_message(self, bus, message):
        """
        handles GStreamer events
        - bus
          bus to listen
        - message
          message to handle
        """
        pass

    def on_open(self, widget):
        """
        handles the event to open a file
        Parameters:
        - widget
          widget that triggered the event
        """
        title = "Choose Audio file"
        action = gtk.FILE_CHOOSER_ACTION_OPEN
        buttons = ( gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, gtk.STOCK_OPEN, gtk.RESPONSE_OK)
        chooser = gtk.FileChooserDialog(title, None, action, buttons)
        chooser.set_default_response(gtk.RESPONSE_OK)
        filefilter = gtk.FileFilter()
        filefilter.set_name("Audio file")
        filefilter.add_pattern("*.mp3")
        filefilter.add_pattern("*.ogg")
        chooser.add_filter(filefilter)
        response = chooser.run()
        if response == gtk.RESPONSE_OK:
            self.set_filename(chooser.get_filename())
        chooser.destroy()

    def on_play_stop(self, widget):
        """
        handles the event to play or stop the media file
        Parameters:
        - widget
          widget that triggered the event
        """
        if self._player:
            # TODO: implement stop to play
            pass
        else:
            self._player = MediaPlayer(self._media_file)
            self._player.play()
        self.update_widgets()

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
        self._running = False
        # wait for update thread to stop
        time.sleep(2)
        gtk.main_quit()

if __name__ == "__main__":
    window = PlayerWindow()
    if len(sys.argv) > 1:
        window.set_filename(sys.argv[1])
    gtk.main()
