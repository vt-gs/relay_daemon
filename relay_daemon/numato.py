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
                if (not self.tx_q.empty()): #Message for Relay Bank Received
                    msg = self.tx_q.get()
                    print '{:s} | {:s}'.format(self.name, msg)
                    if 'READ' in msg:
# TO DO HERE, ADD ABILITY TO READ JUST ONE RELAY

                        print "Time to read!"
                        self.read_all_relays()
#                        self.rx_q.put(self.state)
                    elif 'WRITE' in msg:
                        print "Time to write!"
                        msg_parse = msg.split(':')[1].split(',')
                        hex_val = msg_parse[2]
                        self.write_all_relays(hex_val)
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
            self.tn = telnetlib.Telnet(self.ip)
            self.tn.read_until("User Name:")
            self.tn.write(self.username.encode("utf-8") + "\n")
            if self.password:
                self.tn.read_until("Password:")
                self.tn.write(self.password.encode("utf-8") + "\n")
            resp = self.tn.read_until('>')
#            print resp
            self.logger.info('Succesful telnet to relay bank: {:s}'.format(self.ip))
            self.connected = True
            print 'Connected!'
        except Exception as e:
            print str(e)
            self.logger.info('Failed to telnet to relay bank: {:s}'.format(self.ip))
            self.logger.warning(str(e))
            self.connected = False
            # Close the telnet session since an error happened
            self.tn.close()

    def disconnect(self):
        pass

    def read_relay(self, rel_num):
        """Read Relay status for given relay number"""
        relay_number = "2"
        print relay_number
        print type(relay_number)

        self.tn.write(("relay on " + str(relay_number) + "\r\n").encode())
        print "Relay ON " + relay_number
        time.sleep(1)
        print self.tn.read_eager()

        self.tn.write(b"relay read "+ str(relay_number).encode("ascii") + b"\r\n")
        time.sleep(1)
        resp = self.tn.read_eager()
        print "\nRelay read " + relay_number + ":" + re.split(br'[&>]', resp)[0].decode()

    def read_all_relays(self):

        print "Reading all"
        msg = "relay readall"
        self.tn.write(msg + "\r\n".encode())
        time.sleep(1)
        resp = self.tn.read_eager().splitlines()[0]
        resp = "RELAY,STATUS," + resp
        print resp

        self.rx_q.put(resp)

#        resp = self.tn.read_until('>')
#        print resp
#        print self.tn.read_some()
#        print self.tn.read_very_eager()
#        print self.tn.read_eager()
#        print self.tn.read_lazy()
#        print self.tn.read_very_lazy()
#        print self.tn.expect(['>'])

#        resp = self.tn.read_until('>').strip('\r\n>')
#        self.state = int(resp)
#        return resp

    def set_relay(self, rel_num):
        pass

    def write_all_relays(self, hex_val):
#        print "We'll be reading soon"
#        print hex_val
        msg = "relay writeall "+hex_val
#        print msg
        self.tn.write(msg + "\r\n".encode())
        time.sleep(1)
#        print "WROTE?"
        resp = self.tn.read_eager()
#        print resp
        # Let's "return" a status of the relays written
        # TO DO here is probably a check first that the
        # relays were actually written to properly.  But
        # that may be a solution for something that's
        # not yet a problem.
        self.read_all_relays()

    def stop(self):
        print '{:s} Terminating...'.format(self.name)
        self.logger.info('{:s} Terminating...'.format(self.name))
        # Close the telnet connection
        self.tn.close()
        self._stop.set()

    def stopped(self):
        return self._stop.isSet()
