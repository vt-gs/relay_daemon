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
import binascii

from Queue import Queue

class Ethernet_Relay(threading.Thread):
    def __init__ (self, ssid, cfg):
        threading.Thread.__init__(self, name = 'Relay_Thread')
        self._stop      = threading.Event()
        self.ip         = cfg['ip']
        self.username   = cfg['user']
        self.password   = cfg['pass']
        self.ssid       = ssid

        self.logger     = logging.getLogger(self.ssid)
        print "Initializing {}".format(self.name)
        self.logger.info("Initializing {}".format(self.name))

        self.connected  = False
        self.tn         = None
        self.tx_q       = Queue() #messages into thread
        self.rx_q       = Queue() #messages from thread

    def run(self):
        print "{:s} Started...".format(self.name)
        self.logger.info('Launched {:s}'.format(self.name))
        if (not self.connected):
            self.connect()
        while (not self._stop.isSet()):
            if self.connected:
                print "connected!"
                if (not self.tx_q.empty()): #Message for Relay Bank Received
                    msg = self.tx_q.get()
                    print '{:s} | {:s}'.format(self.name, msg)
                    if 'READ' in msg:
                        print "Time to read!"
                        self.read_all_relays()
                        self.rx_q.put(self.state)
            else:
                time.sleep(5)
                print "Trying to reconnect..."
                self.connect()

            time.sleep(0.01) #Needed to throttle CPU

        self.logger.warning('{:s} Terminated'.format(self.name))
        sys.exit()

    def connect(self):
        try:
            self.logger.info('Attempting to telnet to relay bank: {:s}'.format(self.ip))
            print "one"
            self.tn = telnetlib.Telnet(self.ip)
            print "Object create"
            self.tn.read_until("User Name: ")
            print "Read use name"
            self.tn.write(self.username + "\n")
            print 'entered login'
            if self.password:
                print "waiting for password"
                self.tn.read_until("Password: ")
                print "Found password"
                self.tn.write(self.password + "\n")
            print "waiting for prompt"
            resp = self.tn.read_until('>')
            print "Found prompt"
            print resp
            self.logger.info('Succesful telnet to relay bank: {:s}'.format(self.ip))
            self.connected = True
            print 'Connected!'
        except Exception as e:
            print str(e)
            self.logger.info('Failed to telnet to relay bank: {:s}'.format(self.ip))
            self.connected = False

    def disconnect(self):
        pass

    def read_relay(self, rel_num):
        """Read Relay status for given relay number"""
        pass

    def read_all_relays(self):
        msg = "relay readall\n"
        self.tn.write(msg)
        resp = self.tn.read_until('>').strip('\r\n>')
        self.state = int(resp)
        return self.state

    def set_relay(self, rel_num):
        pass

    def relay_write_all(self):
        pass

    def stop(self):
        print '{:s} Terminating...'.format(self.name)
        self.logger.info('{:s} Terminating...'.format(self.name))
        self._stop.set()

    def stopped(self):
        return self._stop.isSet()
