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

import telnetlib
import threading
import logging

from Queue import Queue

class Ethernet_Relay(threading.Thread):
    def __init__ (self, args):
        threading.Thread.__init__(self, name = 'Relay_Thread')
        self._stop      = threading.Event()
        self.ip         = args.rel_ip
        self.username   = args.rel_user
        self.password   = args.rel_pass
        self.logger     = logging.getLogger(args.ssid)

        self.connected  = False
        self.tn         = None
        self.q          = Queue()

    def run(self):
        self.logger.info('Launching Relay Thread')
        if (not self.connected):
            self.connect()
        while (not self._stop.isSet()):
            if (not self.q.empty()): #Message for Relay Bank Received
                msg = self.q.get()
                print msg

        self.logger.warning('{:s} Terminating...'.format(self.name))
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
            self.logger.info('Succesful telnet to relay bank: {:s}'.format(self.ip, ))
            self.connected = True
            print 'Connected!'
        except:
            self.connected = False

    def stop(self):
        print '{:s} Terminating...'.format(self.name)
        self.logger.info('{:s} Terminating...'.format(self.name))
        self._stop.set()

    def stopped(self):
        return self._stop.isSet()
