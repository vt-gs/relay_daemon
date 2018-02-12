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
from rabbitcomms import BrokerConsumer
from rabbitcomms import BrokerProducer

class Consumer(BrokerConsumer):
    def __init__(self, cfg, loggername=None):
        super(Consumer, self).__init__(cfg, loggername)
        self.cb = None
        self.q  = Queue()

    def process_message(self, method, properties, body):
        msg = 'Received message {:s} from {:s} {:s}'.format(str(method.delivery_tag), str(properties.app_id), str(body))
        self.q.put(msg)

class Service_Thread(threading.Thread):
    def __init__ (self, ssid, cfg):
        threading.Thread.__init__(self, name = 'Service_Thread')
        self._stop  = threading.Event()
        self.ssid   = ssid
        self.cfg    = cfg

        self.rx_q   = Queue() #MEssages received from Broker, command
        self.tx_q   = Queue() #Messages sent to broker, feedback

        self.consumer = Consumer(cfg, loggername=self.ssid)
        self.consume_thread = threading.Thread(target=self.consumer.run, name = 'Serv_Consumer')
        self.consume_thread.daemon = True

        self.producer = BrokerProducer(cfg, loggername=self.ssid)
        self.produce_thread = threading.Thread(target=self.producer.run, name = 'Serv_Producer')
        self.produce_thread.daemon = True

        self.connected = False

        self.logger = logging.getLogger(self.ssid)
        print "Initializing {}".format(self.name)
        self.logger.info("Initializing {}".format(self.name))


    def run(self):
        print "{:s} Started...".format(self.name)
        self.logger.info('Launched {:s}'.format(self.name))

        #Start consumer
        self.consume_thread.start()
        #star producer
        self.produce_thread.start()
        while (not self._stop.isSet()):
            if (self.consumer.connected and self.producer.connected):
                self.connected = True
            else:
                self.connected = False

            if self.connected:
                if (not self.consumer.q.empty()): #received a message on command q
                    rx_msg = self.consumer.q.get()
                    self.rx_q.put(rx_msg)
                elif (not self.tx_q.empty()):#essage to send
                    tx_msg = self.tx_q.get()
                    self.producer.send(tx_msg)

            time.sleep(0.01)#needed to throttle


        self.consumer.stop_consuming()
        self.producer.stop_producing()
        time.sleep(1)
        self.consumer.stop()
        self.producer.stop()
        self.logger.warning('{:s} Terminated'.format(self.name))
        sys.exit()

    def stop(self):
        print '{:s} Terminating...'.format(self.name)
        self.logger.info('{:s} Terminating...'.format(self.name))
        self._stop.set()

    def stopped(self):
        return self._stop.isSet()
