#!/usr/bin/env python
#########################################
#   Title: Main Thread                  #
# Project: VTGS Relay Control Daemon    #
# Version: 1.0                          #
#    Date: Dec 8, 2015                  #
#  Author: Zach Leffke, KJ4QLP          #
# Comment: This is the initial version  # 
#          of the Relay Control Daemon. #
#########################################

import threading
import os
import math
import sys
import string
import time
import socket

from optparse import OptionParser
from datetime import datetime as date
from remote_relay import *

def getTimeStampGMT(self):
    return str(date.utcnow()) + " UTC | "

class request(object):
    def __init__ (self, userid = None, ssid = None, devid = None, state = None, addr=None):
        self.userid = userid
        self.ssid   = ssid
        self.devid  = devid
        self.state  = state
        self.addr   = addr

class relay(object):
    def __init__ (self, fields):
        self.id     = fields[0]
        self.type   = fields[1]
        self.bank   = fields[2]
        self.device = fields[3]
        self.state  = False
        self.val    = 0
        self.ssid   = fields[4].split(';')

class Main_Thread(threading.Thread):
    def __init__ (self, options):
        threading.Thread.__init__(self)
        self._stop  = threading.Event()
        self.ip     = options.serv_ip
        self.port   = options.serv_port
        self.sock   = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.config_file = 'relay.config'
        self.userid = None

        self.ssid_list  = ['VHF', 'UHF', 'LBAND', 'SBAND', 'RAEME', 'WX', 'RELAY']
        self.devid_list = ['USRP', 'LNA', 'POL', 'PTT', 'TRACK', 'RF', 'ALL']
        self.state_list = ['EN', 'DIS', 'QUERY']

        self.req    = request()
        self.valid  = False
        self.lock   = threading.Lock()
        
        self.relays = [] #list to hold 'relay' objects

        self.relay  = remote_relay(options.rel_ip, options.rel_port)
        self.spdt   = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]   #list to hold spdt relay states
        self.dpdt   = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]   #list to hold dpdt relay states
        self.spdt_a_value   = 0   #SPDT BANK A Value, 0-255
        self.spdt_b_value   = 0   #SPDT BANK B Value, 0-255
        self.dpdt_a_value   = 0   #DPDT BANK A Value, 0-255
        self.dpdt_b_value   = 0   #DPDT BANK B Value, 0-255
        self.relays_cmd     = [0,0,0,0] #Contains commanded values for formatting set_relay_msg
        self.relays_fb      = [0,0,0,0] #current relay state
        self.Read_Config()

        for i in range(len(self.relays)):
            print self.relays[i].id, self.relays[i].type, self.relays[i].bank, self.relays[i].device, self.relays[i].val, self.relays[i].ssid

    def Read_Config(self):
        path = os.getcwd() + '/' + self.config_file         
        if os.path.isfile(path) == True:
            param_f = open(path, 'r')
            param_data = param_f.read()
            param_data = param_data.strip()
            param_f.close()
            param_list = param_data.split('\n')
        print len(param_list)
        for i in range(len(param_list)-1):
            self.relays.append(relay(param_list[i+1].split(',')))
        for i in range(8):
            self.relays[i+0].val = int(math.pow(2,i))
            self.relays[i+8].val = int(math.pow(2,i))
            self.relays[i+16].val = int(math.pow(2,i))
            self.relays[i+24].val = int(math.pow(2,i))

    def run(self):
        print self.utc_ts() + "UPDATE   | Main Thread Started..."
        self.sock.bind((self.ip, self.port))
        self.relay.connect()
        self.Read_Relay_State() # get current state of relays after initial connection
        while (not self._stop.isSet()):
            #self.lock.acquire()
            data, addr = self.sock.recvfrom(1024) # buffer size is 1024 bytes
            print "{}IO       | received message: {} from: {}".format(self.utc_ts(), data, addr)
            #print self.utc_ts() + "   received from:", addr
            #print self.utc_ts() + "received message:", data
            #self.valid = self.Check_Request(data)
            if (self.Check_Request(data)) == True:
                self.Read_Relay_State()
                if self.req.state == 'QUERY':
                    self.Process_Query()
                elif self.req.state == 'EN':
                    pass
                elif self.req.state == 'DIS':
                    pass
                self.Process_Request(addr)
            
            #self.lock.release()
        sys.exit()

    def Process_Query(self):
        #Daemon should already know the state of all relays
        if self.req.devid == 'RF': #process RF Query for ssid
            pass
            for i in range(len(self.relays)):
                if self.relays[i].state == True:
                    self.Send_Query_Response(self.relays[i])
            #some_func(self.req.ssid)
        elif self.req.devid == 'ALL': # process All Query for ssid
            pass
            #some_func(self.req.ssid)
        else: #process query for single relay
            pass

    def Send_Query_Response(self, rel):
        print self.req

    def Read_Relay_State(self):
        rel = self.relay.get_relays()
        if (a != -1): 
            mask = 0b00000001
            for i in range(8):
                #SPDT A
                if ((rel[0]>>i) & mask): self.relays[i].state = True
                else: self.relays[i].state = False
                #SPDT B
                if ((rel[1]>>i) & mask): self.relays[i+8].state = True
                else: self.relays[i+8].state = False
                #DPDT A
                if ((rel[2]>>i) & mask): self.relays[i+16].state = True
                else: self.relays[i+16].state = False
                #DPDT B
                if ((rel[3]>>i) & mask): self.relays[i+24].state = True
                else: self.relays[i+24].state = False

    def Check_Relay_States(self):
        self.spdt_a = 0
        self.spdt_b = 0
        self.dpdt_a = 0
        self.dpdt_b = 0
        for i in range(8):
            if self.relays[i+0 ].state == True:  self.spdt_a += self.relays[i].val
            if self.relays[i+8 ].state == True:  self.spdt_b += self.relays[i].val
            if self.relays[i+16].state == True:  self.dpdt_a += self.relays[i].val
            if self.relays[i+24].state == True:  self.dpdt_b += self.relays[i].val
            

    def Process_Request(self, data, addr):
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
                self.req.addr = addr
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


