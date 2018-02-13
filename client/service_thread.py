#!/usr/bin/env python
#############################################
#   Title: Relay Client Service Thread      #
# Project: VTGS Relay Control Daemon        #
# Version: 2.0                              #
#    Date: Dec 15, 2017                     #
#  Author: Zach Leffke, KJ4QLP              #
# Comment:                                  #
#   -Relay Control Client Service Thread    #
#                                           #
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
        self.q  = Queue() #place received messages here.

    def process_message(self, method, properties, body):
        msg = 'Received message {:s} from {:s} {:s}'.format(str(method.delivery_tag), str(properties.app_id), str(body))
        self.q.put(msg)

    def get_connection_state(self):
        return self.connected

class Producer(BrokerProducer):
    def __init__(self, cfg, loggername=None):
        super(Producer, self).__init__(cfg, loggername)

    def get_connection_state(self):
        return self.connected


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

        self.producer = Producer(cfg, loggername=self.ssid)
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
            if (self.consumer.get_connection_state() and self.producer.get_connection_state()):
                self.connected = True
            else:
                self.connected = False

            print self.connected

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

    def get_connection_state(self):
        return self.connected

    def stop(self):
        print '{:s} Terminating...'.format(self.name)
        self.logger.info('{:s} Terminating...'.format(self.name))
        self._stop.set()

    def stopped(self):
        return self._stop.isSet()
