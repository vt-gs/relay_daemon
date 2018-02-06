#!/usr/bin/env python
#############################################
#   Title: Relay Daemon Service Thread      #
# Project: VTGS Relay Control Daemon        #
# Version: 2.0                              #
#    Date: Dec 15, 2017                     #
#  Author: Zach Leffke, KJ4QLP              #
# Comment:                                  #
#   -Relay Control Daemon Service Thread    #
#   -This is the User interface             #
#############################################

import threading
import time
import pika

from Queue import Queue
from logger import *
import rabbitcomms

class Service_Thread(threading.Thread):
    def __init__ (self, args):
        threading.Thread.__init__(self, name = 'Service_Thread')
        self._stop  = threading.Event()
        self.args   = args
        self.ssid   = args.ssid

        self.ip     = args.broker_ip
        self.port   = args.broker_port

        self.q      = Queue()
        self.state  = 'BOOT'

        self.producer = None
        self.consumer = None

        self.logger = logging.getLogger(self.ssid)
        print "Initializing {}".format(self.name)
        self.logger.info("Initializing {}".format(self.name))

    def run(self):
        print "{:s} Started...".format(self.name)
        self.logger.info('Launched {:s}'.format(self.name))
        try:
            #Connect to RabbitMQ Broker
            self.logger.info("Attempting to Connect to Rabbit MQ Broker: [{}:{}]".format(self.ip, self.port))
            print "Connected to Rabbit MQ Broker: [{}:{}]".format(self.ip, self.port)
        except Exception as e:
            print 'Some other Exception occurred:', e
            self.logger.info("Could not set up Service data on: {}:{}".format(self.ip, self.port))
            self.logger.info(e)
            sys.exit()

        while (not self._stop.isSet()):
            try:
                #data, addr = self.rx_sock.recvfrom(1024)
                data, addr= self.rx_sock.recvfrom(1024)
                data = data.strip('\n')
                if data:
                    #print addr, data
                    print "\n[{:s}:{:d}]->[{:s}:{:d}] Received User Message: {:s}".format(addr[0], addr[1], self.ip, self.port, data)
                    self.logger.info("[{:s}:{:d}]->[{:s}:{:d}] Received User Message: {:s}".format(addr[0], addr[1], self.ip, self.port, data))
                    self.q.put(data)
            except socket.error, v:
                errorcode=v[0]
                #print v
                if errorcode==errno.EWOULDBLOCK:  #Expected, No data on uplink
                    #print 'socket timeout'
                    pass
            except Exception as e:
                print 'Some other Exception occurred:', e
                self.logger.info(e)

            time.sleep(0.01) #Needed to throttle CPU

        self.rx_sock.close()
        self.logger.warning('{:s} Terminated'.format(self.name))
        sys.exit()

    def _send_resp(self, msg):
        print "{:s} | Sending Response: {:s}".format(self.name, str(msg))

    def stop(self):
        print '{:s} Terminating...'.format(self.name)
        self.logger.info('{:s} Terminating...'.format(self.name))
        self._stop.set()

    def stopped(self):
        return self._stop.isSet()
