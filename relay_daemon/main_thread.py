#!/usr/bin/env python
#############################################
#   Title: Relay Daemon Main Thread         #
# Project: VTGS Relay Control Daemon        #
# Version: 2.0                              #
#    Date: Dec 15, 2017                     #
#  Author: Zach Leffke, KJ4QLP              #
# Comment:                                  #
#   -Relay Control Daemon Main Thread       #
#   -Intended for use with systemd          #
#############################################

import threading
import time

from logger import *
import numato
import service_thread

class Main_Thread(threading.Thread):
    def __init__ (self, args):
        threading.Thread.__init__(self, name = 'Main_Thread')
        self._stop      = threading.Event()
        self.args = args
        self.ssid = args.ssid

        self.state  = 'BOOT' #BOOT, STANDBY, ACTIVE, WX, FAULT

        #setup logger
        self.main_log_fh = setup_logger(self.ssid, ts=args.startup_ts, log_path=args.log_path)
        self.logger = logging.getLogger(self.ssid) #main logger

    def run(self):
        print "{:s} Started...".format(self.name)
        self.logger.info('Launched {:s}'.format(self.name))
        try:
            while (not self._stop.isSet()):
                if self.state == 'BOOT':
                    #Daemon activating for the first time
                    #Activate all threads
                    #State Change:  BOOT --> STANDBY
                    #All Threads Started
                    if self._init_threads():#if all threads activate succesfully
                        
                        self.logger.info('Successfully Launched Threads, Switching to STANDBY State')
                        self.set_state('STANDBY')
                    else:
                        self.set_state('FAULT', 'Failed to Launch Threads')
                    pass
                elif self.state == 'STANDBY':
                    pass
                elif self.state == 'WX':
                    pass
                elif self.state == 'ACTIVE':
                    #Describe ACTIVE here
                    #read uplink Queue from C2 Radio thread
                    #print 'ACTIVE'
                    if (not self.service_thread.q.empty()):
                        msg = self.service_thread.q.get()
                        print '{:s} | Service Thread RX Message: {:s}'.format(self.name, msg)
                        self.relay_thread.tx_q.put(msg)
                    if (not self.relay_thread.rx_q.empty()):
                        rel_msg = self.relay_thread.rx_q.get()
                        print '{:s} | Relay rx_q message: {:s}'.format(self.name, str(rel_msg))
                        self._send_service_resp(rel_msg)

                    #print "Querying relays"
                    #rel_state, rel_int = self.relay_thread.read_all_relays()
                    #print rel_state, rel_int
                    #time.sleep(1)
                    pass

                time.sleep(0.01) #Needed to throttle CPU

        except (KeyboardInterrupt, SystemExit): #when you press ctrl+c
            print "\nCaught CTRL-C, Killing Threads..."
            self.logger.warning('Caught CTRL-C, Terminating Threads...')
            self.relay_thread.stop()
            self.relay_thread.join() # wait for the thread to finish what it's doing
            self.service_thread.stop()
            self.service_thread.join() # wait for the thread to finish what it's doing
            self.logger.warning('Terminating {:s}...'.format(self.name))
            sys.exit()
        sys.exit()

    def _send_service_resp(self,msg):
        self.service_thread._send_resp(msg)



    def set_state(self, state, error=None):
        self.state = state
        self.logger.info('Changed STATE to: {:s}'.format(self.state))
        if self.state == 'BOOT':
            pass
        if self.state == 'STANDBY':
            pass
        if self.state == 'ACTIVE':
            time.sleep(1)
        if self.state == 'WX':
            pass
        if self.state == 'FAULT':
            pass
            time.sleep(10)

    def _init_threads(self):
        try:
            #Initialize Relay Thread
            self.logger.info('Setting up Relay_Thread')
            self.relay_thread = numato.Ethernet_Relay(self.args)
            self.relay_thread.daemon = True

            #Initialize Server Thread
            self.logger.info('Setting up Service_Thread')
            self.service_thread = service_thread.Service_Thread(self.args)
            self.service_thread.daemon = True

            #Launch threads
            self.logger.info('Launching Relay_Thread')
            self.relay_thread.start() #non-blocking

            self.logger.info('Launching Service_Thread')
            self.service_thread.start() #non-blocking

            return True
        except Exception as e:
            self.logger.warning('Error Launching Threads:')
            self.logger.warning(str(e))
            self.logger.warning('Setting STATE --> FAULT')
            self.state = 'FAULT'
            return False

    def stop(self):
        print '{:s} Terminating...'.format(self.name)
        self.logger.info('{:s} Terminating...'.format(self.name))
        self._stop.set()

    def stopped(self):
        return self._stop.isSet()
