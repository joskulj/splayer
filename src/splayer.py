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

    def is_playing(self):
        """
        checks if the file is currently played
        Returns:
        - True:  file is played
        - False: file is not played
        """
        return self._playing

    def play(self, player):
        """
        plays the file
        Parameters:
        - player
          GStreamer player to use
        """
        self._player = player
        self._player.set_property("uri", self.get_uri())
        self._player.set_state(gst.STATE_PLAYING)
        self._playing = True

    def stop(self):
        """
        stops playing the file
        """
        self._player.set_state(gst.STATE_NULL)
        self._player = None
        self._playing = False

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

class MediaPlayer(object):
    """
    class to play a media file
    """

    def __init__(self, filename):
        """
        creates an instance
        Parameters:
        - filename
          file to play
        """
        self._filename = filename
        self._pipeline = None
        if self._filename.lower().endswith("mp3"):
            self._pipeline = self.create_mp3_pipeline()
        if self._filename.lower().endswith("ogg"):
            self._pipeline = self.create_ogg_pipeline()
        if not self._pipeline:
            print "media file not supported"

    def create_mp3_pipeline(self):
        """
        creates a pipeline to play MP3 files
        """
        pipeline = gst.Pipeline("PlayerPipeline")
        source = gst.element_factory_make("filesrc", "file-source")
        source.set_property("location", self._filename)
        pipeline.add(source)
        decoder = gst.element_factory_make("mad", "decoder")
        pipeline.add(decoder)
        source.link(decoder)
        converter = gst.element_factory_make("audioconvert", "converter")
        pipeline.add(converter)
        decoder.link(converter)
        sink = gst.element_factory_make("autoaudiosink", "audio-output")
        pipeline.add(sink)
        decoder.link(sink)
        return pipeline

    def create_ogg_pipeline(self):
        """
        creates a pipeline to play ogg files
        """
        pipeline = gst.Pipeline("PlayerPipeline")
        source = gst.element_factory_make("filesrc", "file-source")
        source.set_property("location", self._filename)
        pipeline.add(source)
        demuxer = gst.element_factory_make("oggdemux", "demuxer")
        # implement demuxer callback (?)
        pipeline.add(demuxer)
        source.link(demuxer)
        decoder = gst.element_factory_make("vorbisdec", "vorbis-decoder")
        pipeline.add(decoder)
        demuxer.link(decoder)
        converter = gst.element_factory_make("audioconvert", "converter")
        pipeline.add(converter)
        decoder.link(converter)
        sink = gst.element_factory_make("autoaudiosink", "audio-output")
        pipeline.add(sink)
        decoder.link(sink)
        return pipeline

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

    def get_position(self):
        """
        Returns:
        - current playing position
        """
        return self._pipeline.query_position(gst.FORMAT_TIME, None)[0]

class PlayerWindow(object):
    """
    GTK Window for the player
    """

    def __init__(self):
        """
        creates an instance
        """
        self._media_file = MediaFile(None)
        self._widget_tree = self.init_widget_tree()
        self._thread = None
        self.update_widgets()
        self._player = gst.element_factory_make("playbin2", "player")
        fakesink = gst.element_factory_make("fakesink", "fakesink")
        self._player.set_property("video-sink", fakesink)
        bus = self._player.get_bus()
        bus.add_signal_watch()
        bus.connect("message", self.on_message)

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
        # , "on_add_directory" : self.on_add_directory
        # , "on_remove_directory" : self.on_remove_directory
        # , "on_synchronize" : self.on_synchronize
        # , "on_exit" : self.on_exit }
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
            if self._media_file.is_playing():
                play_button.set_label("_Stop")
            else:
                play_button.set_label("_Play")
            label.set_text(self._media_file.get_filename())
        else:
            play_button.set_sensitive(False)
            label.set_text("")

    def set_filename(self, filename):
        """
        sets the filename
        Parameters:
        - filename
          filename to set
        """
        self._media_file = MediaFile(filename)
        self.update_widgets()

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
        if self._media_file.is_playing():
            self._media_file.stop()
        else:
            self._media_file.play(self._player)
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
        gtk.main_quit()

class PlayerWindowThread(object):
    """
    thread to syncronize the files
    """

    def __init__(self):
        """
        creates an instance
        """
        self._state = STATE_NOT_STARTED
        self._sleep_interval = 10

    def is_running(self):
        """
        Returns:
        - True:  server is running
        - False: server is not running
        """
        return self._state != STATE_STOPPING

    def stop(self):
        """
        signals the thread to stop
        """
        self._state = STATE_STOPPING

    def start_pausing(self):
        """
        signals the thread to pause
        """
        self._state = STATE_PAUSING

    def stop_pausing(self):
        """
        signals the thread to stop pausing
        """
        self._state = STATE_RUNNING

    def start(self):
        """
        starts the thread
        """
        self._state = STATE_RUNNING
        while self.is_running():
            print "loop entered."
            if self._state == STATE_RUNNING:
                print "SyncThread running."
            if self._state == STATE_PAUSING:
                print "SyncThread paused."
            print "sleep"
            time.sleep(self._sleep_interval)
            print "wake up"
        print "SyncThread stopped."
        #if self._state == STATE_NOT_STARTED:
        #    self._state = STATE_RUNNING
        #    if self._state != STATE_STOPPING:
        #        # TODO: implement file synchronization
        #        if self._state == STATE_RUNNING:
        #            print "DaemonSyncThread running"
        #        if self._state == STATE_PAUSING:
        #            print "DaemonSyncThread paused"
        #        # time.sleep(self._sleep_interval)
        #    print "SyncThread stopped."


if __name__ == "__main__":
    # gtk.gdk.threads_init()
    window = PlayerWindow()
    if len(sys.argv) > 1:
        window.set_filename(sys.argv[1])
    gtk.main()
