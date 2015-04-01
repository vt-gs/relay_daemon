#!/usr/bin/env python
import socket
import os
import string
import sys
import time
import threading
from remote_relay import *

class Data_Thread(threading.Thread):
    def __init__ (self, options):
        threading.Thread.__init__(self)
        self._stop = threading.Event()
        self.ip = options.ip
        self.port = options.port
        self.suspend = False
        self.relay = remote_relay(self.ip, self.port)
        

    def run(self):
        #self.sock.bind((self.ip, self.port))
        while (not self._stop.isSet()):
            pass
        sys.exit()

    def send_msg(self):
        
        pass
        

    def connect(self):
        print "Data Thread:  Connecting..."
        try:
            self.sock.connect((self.ip, self.port))
        except ValueError:
            print "Connection Failed, Socket Exception"
            sys.exit()

    def stop(self):
        self._stop.set()

    def stopped(self):
        return self._stop.isSet()
