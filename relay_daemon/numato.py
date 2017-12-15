#!/usr/bin/env python
#############################################
#   Title: Numato Ethernet Relay Interface  #
# Project: VTGS Relay Control Daemon        #
# Version: 2.0                              #
#    Date: Dec 15, 2017                     #
#  Author: Zach Leffke, KJ4QLP              #
# Comment:                                  #
#   -Relay Control Daemon                   #
#   -Intended for use with systemd          #
#############################################

import datetime
import telnetlib
from Queue import Queue

import threading

class Ethernet_Relay(threading.Thread):
    def __init__ (self, args):
        threading.Thread.__init__(self)
        self._stop      = threading.Event()
        self.ip         = args.rel_ip
        self.username   = args.rel_user
        self.password   = args.rel_pass
        self.connected  = False
        self.tn         = None
        self.q          = Queue()

    def run(self):
        if (not self.connected):
            self.connect()
        while (not self._stop.isSet()):
            if (not self.q.empty()): #Message for Relay Bank Received
                msg = self.q.get()
                print msg

    def connect(self):
        self.tn = telnetlib.Telnet(self.ip)
        self.tn.read_until("User Name: ")
        self.tn.write(self.username + "\n")
        print 'entered login'
        if self.password:
            self.tn.read_until("Password: ")
            self.tn.write(self.password + "\n")
        self.connected = True
        print 'Connected!'

    def stop(self):
        self._stop.set()

    def stopped(self):
        return self._stop.isSet()
