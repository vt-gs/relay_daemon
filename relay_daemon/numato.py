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

import sys
import telnetlib
import threading
import logging
import time

from Queue import Queue

class Ethernet_Relay(threading.Thread):
    def __init__ (self, args):
        threading.Thread.__init__(self, name = 'Relay_Thread')
        self._stop      = threading.Event()
        self.ip         = args.rel_ip
        self.username   = args.rel_user
        self.password   = args.rel_pass
        self.ssid       = args.ssid

        self.logger     = logging.getLogger(self.ssid)
        print "Initializing {}".format(self.name)
        self.logger.info("Initializing {}".format(self.name))

        self.connected  = False
        self.tn         = None
        self.q          = Queue()

    def run(self):
        print "{:s} Started...".format(self.name)
        self.logger.info('Launched {:s}'.format(self.name))
        if (not self.connected):
            self.connect()
        while (not self._stop.isSet()):
            if self.connected:
                if (not self.q.empty()): #Message for Relay Bank Received
                    msg = self.q.get()
                    print '{:s} | {:s}'.format(self.name, msg)
            else:
                time.sleep(5)
                self.connect()

            time.sleep(0.01) #Needed to throttle CPU

        self.logger.warning('{:s} Terminated'.format(self.name))
        sys.exit()

    def connect(self):
        try:
            self.tn = telnetlib.Telnet(self.ip)
            self.tn.read_until("User Name: ")
            self.tn.write(self.username + "\n")
            print 'entered login'
            if self.password:
                self.tn.read_until("Password: ")
                self.tn.write(self.password + "\n")
            self.logger.info('Succesful telnet to relay bank: {:s}'.format(self.ip))
            self.connected = True
            print 'Connected!'
        except:
            self.logger.info('Failed to telnet to relay bank: {:s}'.format(self.ip))
            self.connected = False

    def stop(self):
        print '{:s} Terminating...'.format(self.name)
        self.logger.info('{:s} Terminating...'.format(self.name))
        self._stop.set()

    def stopped(self):
        return self._stop.isSet()
