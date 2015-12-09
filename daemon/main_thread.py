#!/usr/bin/env python
##################################################
# GPS Interface
# Author: Zach Leffke
# Description: Initial GPS testing
##################################################

import threading
import os
import math
import sys
import string
import time
import socket

from optparse import OptionParser
from datetime import datetime as date
from relay_thread import *

def getTimeStampGMT(self):
    return str(date.utcnow()) + " UTC | "

class request(object):
<<<<<<< HEAD
    def __init__ (self, userid = None, ssid = None, devid = None, state = None):
        self.userid = userid
        self.ssid   = ssid
        self.devid  = devid
        self.state  = state

class group(object):
    def __init__ (self, userid = None, ssid = None, devid = None, state = None):
        self.userid = userid
        self.ssid   = ssid
        self.devid  = devid
        self.state  = state
=======
    def __init__ (self, user = None, cmd = None, az = None, el = None):
        self.user   = user
        self.cmd    = cmd
        self.az     = az
        self.el     = el
>>>>>>> 4f7ba02c59b32670df11047e29b633a33d82476f

class Main_Thread(threading.Thread):
    def __init__ (self, options):
        threading.Thread.__init__(self)
        self._stop  = threading.Event()
        self.ip     = options.serv_ip
        self.port   = options.serv_port
        self.sock   = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        self.ssid_list  = ['VHF', 'UHF', 'LBAND', 'SBAND', 'RAEME', 'WX', 'RELAY']
        self.devid_list = ['USRP', 'LNA', 'POL', 'PTT', 'TRACK', 'RF', 'ALL']
        self.state_list = ['EN', 'DIS', 'QUERY']

        self.req    = request()
        self.valid  = False
        self.lock   = threading.Lock()

<<<<<<< HEAD
        self.relay  = remote_relay(options.rel_ip, options.rel_port)
        self.spdt   = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]   #list to hold spdt relay states
        self.dpdt   = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]   #list to hold dpdt relay states
        self.spdt_a_value   = 0   #SPDT BANK A Value, 0-255
        self.spdt_b_value   = 0   #SPDT BANK B Value, 0-255
        self.dpdt_a_value   = 0   #DPDT BANK A Value, 0-255
        self.dpdt_b_value   = 0   #DPDT BANK B Value, 0-255
        self.relays_cmd     = [0,0,0,0] #Contains commanded values for formatting set_relay_msg

        
=======
        #self.rel_thread = MD01_Thread('VUL', options.vul_ip, options.vul_port)
        #self.rel_thread.daemon = True
        #self.rel_thread.start()
        #time.sleep(0.1)
>>>>>>> 4f7ba02c59b32670df11047e29b633a33d82476f

    def run(self):
        print self.utc_ts() + "UPDATE   | Main Thread Started..."
        self.sock.bind((self.ip, self.port))
        while (not self._stop.isSet()):
            #self.lock.acquire()
            data, addr = self.sock.recvfrom(1024) # buffer size is 1024 bytes
            #print self.utc_ts() + "   received from:", addr
            #print self.utc_ts() + "received message:", data
            #self.valid = self.Check_Request(data)
            if (self.Check_Request(data)) == True:
                pass
                #self.Process_Request(data, addr)
            #self.lock.release()
        sys.exit()

    def Process_Request(self, data, addr):
        if   self.req.ssid == 'VUL': #VHF/UHF/L-Band subsystem ID
            self.Process_Command(self.vul_thread, data, addr)
        elif self.req.ssid == '3M0': #3.0 m Dish Subsystem ID
            self.Process_Command(self.dish_3m0_thread, data, addr)
        elif self.req.ssid == '4M5': #4.5 m Dish Subsystem ID
            self.Process_Command(self.dish_4m5_thread, data, addr)
        elif self.req.ssid == 'WX':  #NOAA WX Subsystem ID
            pass

    def Process_Command(self, thr, data, addr):
        az = 0 
        el = 0
        if thr.connected == True:
            if   self.req.cmd == 'SET':
                thr.set_position(self.req.az, self.req.el)
                az, el = thr.get_position()
            elif self.req.cmd == 'QUERY':
                az, el = thr.get_position()
                #print az, el
            elif self.req.cmd == 'STOP':
                thr.set_stop()
                time.sleep(0.01)
                az, el = thr.get_position()
            
        self.Send_Feedback(thr, az, el, data, addr)

    def Send_Feedback(self,thr, az, el, data, addr):
        msg = thr.ssid + " QUERY " + str(az) + " " + str(el) + "\n"
        self.sock.sendto(msg, addr)

    def Check_Request(self, data):
        fields = data.split(" ")

        #Check number of fields        
        if len(fields) == 4:
            try:
                self.req = request(fields[0].strip('\n'), fields[1].strip('\n'), fields[2].strip('\n'), fields[3].strip('\n'))
            except ValueError:
                print self.utc_ts() + "IO Error | Invalid Command Data Types"
                return False
        else: 
            print self.utc_ts() + "IO Error | Invalid number of fields in command: ", len(fields) 
            return False

        #Validate Subsystem ID Field
        valid_ssid = False
        for i in range(len(self.ssid_list)): 
            if self.ssid_list[i] == self.req.ssid: valid_ssid = True
        if valid_ssid == False: print self.utc_ts() + ("IO Error | Invalid Subsystem ID: %s, from user: %s" % (self.req.ssid, self.req.userid))
       
        #Validate Device ID Field
        valid_devid = False
        for i in range(len(self.devid_list)): 
            if self.devid_list[i] == self.req.devid: valid_devid = True
        if valid_devid == False: print self.utc_ts() + ("IO Error | Invalid Device ID: %s, from user: %s" % (self.req.devid, self.req.userid))

        #Validate State Field
        valid_state = False
        for i in range(len(self.state_list)): 
            if self.state_list[i] == self.req.state: valid_state = True
        if valid_state == False: print self.utc_ts() + ("IO Error | Invalid State: %s, from user: %s" % (self.req.state, self.req.userid))

        if ((valid_ssid == False) or (valid_devid == False) or (valid_state == False)): return False
        else: return True

    def utc_ts(self):
        return str(date.utcnow()) + " UTC | "

    def stop(self):
        self.gps_ser.close()
        self._stop.set()
        sys.quit()

    def stopped(self):
        return self._stop.isSet()


