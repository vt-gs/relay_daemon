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
    def __init__ (self, userid = None, ssid = None, device = None, state = None, addr=None):
        self.userid = userid
        self.ssid   = ssid
        self.device  = device
        self.state  = state
        self.addr   = addr

class relay(object):
    def __init__ (self, fields):
        self.id     = int(fields[0]) #relay id number, 1-32
        if fields[1] == 'connected':  self.status = True
        else: self.status = False
        #self.status = fields[1] #relay wired status, True = connected or False= not connected
        self.type   = fields[2] #SPDT or DPDT
        self.bank   = fields[3] #A or B
        self.device = fields[4] #What device is connected to relay, LNA, USRP, TRACK, etc.
        self.ssid   = fields[5].split(';') #What subsystems belong to relay
        self.group  = fields[6].split(';') #What relay groups relay belongs to
        self.state  = False     #Relay engaged state (TRUE = ON, FALSE=OFF)
        self.val    = 0         #relay bit value in decimal form (1,2,4,8,etc.)
        self.userid = None      #holds last user to command the relays.

class Main_Thread(threading.Thread):
    def __init__ (self, options):
        threading.Thread.__init__(self)
        self._stop  = threading.Event()
        self.ip     = options.serv_ip
        self.port   = options.serv_port
        self.sock   = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.config_file = 'relay.config'
        self.userid = None

        self.ssid_list  = ['VHF', 'UHF', 'LBAND', 'SBAND', 'RAEME', 'WX', 'ALL']
        self.device_list = ['USRP', 'LNA', 'POL', 'PTT', 'TRACK', 'RF', 'ALL']
        self.state_list = ['EN', 'DIS', 'QUERY']

        self.req    = request()
        self.valid  = False
        self.lock   = threading.Lock()

        self.connected = False
        
        self.relays = [] #list to hold 'relay' objects

        self.relay  = remote_relay(options.rel_ip, options.rel_port)
        self.spdt   = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]   #list to hold spdt relay states
        self.dpdt   = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]   #list to hold dpdt relay states

        self.spdt_a_value   = 0   #SPDT BANK A Value, 0-255
        self.spdt_b_value   = 0   #SPDT BANK B Value, 0-255
        self.dpdt_a_value   = 0   #DPDT BANK A Value, 0-255
        self.dpdt_b_value   = 0   #DPDT BANK B Value, 0-255

        self.relays_cmd     = [0,0,0,0] #Contains commanded values for formatting set_relay_msg
        #self.relays_fb      = [0,0,0,0] #current relay state

        self.Read_Config()

    
    def run(self):
        print self.utc_ts() + "TH | Main Thread Started..."
        self.sock.bind((self.ip, self.port))
        print "{}IO | UDP Server Port Open".format(self.utc_ts())
        self.connected = self.relay.connect()
        if self.connected == True:
            print self.utc_ts() + "TH | Connected To Controller"
            self.Read_Relay_State() # get current state of relays after initial connection
            while (not self._stop.isSet()):
                #self.lock.acquire()
                self.data, self.addr = self.sock.recvfrom(1024) # buffer size is 1024 bytes
                print "{}IO | received message: <{}> from: {}".format(self.utc_ts(), self.data.strip('\n'), self.addr)
                
                if (self.Check_Request(self.data,self.addr)) == True:
                    if self.req.state == 'QUERY':
                        self.Process_Query()
                    elif self.req.state == 'EN':
                        self.Process_Enable()
                    elif self.req.state == 'DIS':
                        self.Process_Disable()
        
        sys.exit()

    def Process_Enable(self):
        if self.req.ssid == 'ALL':
            print self.utc_ts() + ("IO | Error: Subsystem ID: %s, cannot be ENABLED, from user: %s" % (self.req.ssid, self.req.userid))
        else:
            if self.req.device == 'RF': #process RF Query for ssid
                for i in range(len(self.relays)): #cycle through relay list
                    for j in range(len(self.relays[i].ssid)): #cycle through matching SSID
                        if self.relays[i].ssid[j] == self.req.ssid: #verify SSID match
                            for k in range(len(self.relays[i].group)): #cycle through group
                                if self.relays[i].group[k] == self.req.device:
                                    if self.relays[i].state == False:
                                        self.Update_Relay_CMD(self.relays[i], True)
                                        self.Print_Relay(i)
            elif self.req.device == 'ALL': #process RF Query for ssid
                for i in range(len(self.relays)): #cycle through relay list
                    for j in range(len(self.relays[i].ssid)): #cycle through matching SSID
                        if self.relays[i].ssid[j] == self.req.ssid: #verify SSID match
                            for k in range(len(self.relays[i].group)): #cycle through group
                                if self.relays[i].group[k] == self.req.device:
                                    if self.relays[i].state == False:
                                        self.Update_Relay_CMD(self.relays[i], True)
                                        self.Print_Relay(i)
            else:
                for i in range(len(self.relays)):
                    for j in range(len(self.relays[i].ssid)):
                        if self.relays[i].ssid[j] == self.req.ssid:
                            if self.relays[i].device == self.req.device:
                                self.Update_Relay_CMD(self.relays[i], True)
                                self.Print_Relay(i)
    
            print self.utc_ts() + "TH | Relay Command State:",self.relays_cmd
            self.Set_Relay()
            self.Send_Feedback()

    def Process_Disable(self):
        if self.req.ssid == 'ALL':
            print self.utc_ts() + ("IO | Error: Subsystem ID: %s, cannot be DISABLED, from user: %s" % (self.req.ssid, self.req.userid))
        else:
            if self.req.device == 'RF': #process RF Query for ssid
                for i in range(len(self.relays)): #cycle through relay list
                    for j in range(len(self.relays[i].ssid)): #cycle through matching SSID
                        if self.relays[i].ssid[j] == self.req.ssid: #verify SSID match
                            for k in range(len(self.relays[i].group)): #cycle through group
                                if self.relays[i].group[k] == self.req.device:
                                    if self.relays[i].state == True:
                                        self.Update_Relay_CMD(self.relays[i], False)
                                        self.Print_Relay(i)
            elif self.req.device == 'ALL': #process RF Query for ssid
                for i in range(len(self.relays)): #cycle through relay list
                    for j in range(len(self.relays[i].ssid)): #cycle through matching SSID
                        if self.relays[i].ssid[j] == self.req.ssid: #verify SSID match
                            for k in range(len(self.relays[i].group)): #cycle through group
                                if self.relays[i].group[k] == self.req.device:
                                    if self.relays[i].state == True:
                                        self.Update_Relay_CMD(self.relays[i], False)
                                        self.Print_Relay(i)
            else:
                for i in range(len(self.relays)):
                    for j in range(len(self.relays[i].ssid)):
                        if self.relays[i].ssid[j] == self.req.ssid:
                            if self.relays[i].device == self.req.device:
                                self.Update_Relay_CMD(self.relays[i], False)
                                self.Print_Relay(i)

            print self.utc_ts() + "TH | Relay Command State:",self.relays_cmd
            self.Set_Relay()
            self.Send_Feedback()

    def Send_Feedback(self):
        if self.req.device == 'RF': #process RF Query for ssid
            for i in range(len(self.relays)): #cycle through relay list
                for j in range(len(self.relays[i].ssid)): #cycle through matching SSID
                    if self.relays[i].ssid[j] == self.req.ssid: #verify SSID match
                        for k in range(len(self.relays[i].group)): #cycle through group
                            if self.relays[i].group[k] == self.req.device:
                                self.Print_Relay(i)
                                self.Send_Query_Feedback(self.req.userid, self.relays[i].ssid[j], self.relays[i].device, str(self.relays[i].state))
        elif self.req.device == 'ALL': #process RF Query for ssid
            for i in range(len(self.relays)): #cycle through relay list
                for j in range(len(self.relays[i].ssid)): #cycle through matching SSID
                    if self.relays[i].ssid[j] == self.req.ssid: #verify SSID match
                        for k in range(len(self.relays[i].group)): #cycle through group
                            if self.relays[i].group[k] == self.req.device:
                                self.Print_Relay(i)
                                self.Send_Query_Feedback(self.req.userid, self.relays[i].ssid[j], self.relays[i].device, str(self.relays[i].state))
        else: #process query for single relay
            for i in range(len(self.relays)):
                for j in range(len(self.relays[i].ssid)):
                    if self.relays[i].ssid[j] == self.req.ssid:
                        if self.relays[i].device == self.req.device:
                            self.Print_Relay(i)
                            self.Send_Query_Feedback(self.req.userid, self.relays[i].ssid[j], self.relays[i].device, str(self.relays[i].state))
        

    def Set_Relay(self):
        print self.utc_ts() + "TH | Relay Command State:",self.relays_cmd
        rel = self.relay.set_relays(self.relays_cmd)
        if (rel != -1): self.Update_Relay_State(rel) 

    def Update_Relay_CMD(self, rel, inc):
        idx = 0
        if ((rel.id >=1)  and (rel.id <=8)) :  idx = 0
        if ((rel.id >=9)  and (rel.id <=16)):  idx = 1
        if ((rel.id >=17) and (rel.id <=24)):  idx = 2
        if ((rel.id >=25) and (rel.id <=32)):  idx = 3

        if   inc == True : 
            self.relays_cmd[idx] += rel.val
        elif inc == False: 
            self.relays_cmd[idx] -= rel.val

    def Print_Relay(self, i):
        print self.utc_ts() + "TH |", self.relays[i].id, self.relays[i].status, self.relays[i].type, self.relays[i].bank, \
              self.relays[i].device, self.relays[i].val, self.relays[i].state,self.relays[i].ssid,self.relays[i].group

    def Read_Relay_State(self):
        rel = self.relay.get_relays()
        if (rel != -1): self.Update_Relay_State(rel)

    def Update_Relay_State(self, rel):
        mask = 0b00000001
        self.relays_cmd = [0,0,0,0]
        for i in range(8):
            #SPDT A
            if ((rel[0]>>i) & mask): self.relays[i].state = True
            else: self.relays[i].state = False
            if self.relays[i].state == True:  self.relays_cmd[0] += self.relays[i].val
            #SPDT B
            if ((rel[1]>>i) & mask): self.relays[i+8].state = True
            else: self.relays[i+8].state = False
            if self.relays[i+8].state == True:  self.relays_cmd[1] += self.relays[i+8].val
            #DPDT A
            if ((rel[2]>>i) & mask): self.relays[i+16].state = True
            else: self.relays[i+16].state = False
            if self.relays[i+16].state == True:  self.relays_cmd[2] += self.relays[i+16].val
            #DPDT B
            if ((rel[3]>>i) & mask): self.relays[i+24].state = True
            else: self.relays[i+24].state = False
            if self.relays[i+24].state == True:  self.relays_cmd[3] += self.relays[i+24].val
        print self.utc_ts() + "TH | Relay Command State:",self.relays_cmd

    def Check_Request(self, data,addr):
        fields = data.strip('\n').split(" ")

        #Check number of fields        
        if len(fields) == 4:
            try:
                self.req = request(fields[0].strip('\n'), fields[1].strip('\n'), fields[2].strip('\n'), fields[3].strip('\n'))
                self.req.addr = addr
            except ValueError:
                print self.utc_ts() + "IO | Error: Invalid Command Data Types"
                return False
        else: 
            print self.utc_ts() + "IO | Error: Invalid number of fields in command: ", len(fields) 
            return False

        #Validate Subsystem ID Field
        valid_ssid = False
        for i in range(len(self.ssid_list)): 
            if self.ssid_list[i] == self.req.ssid: valid_ssid = True
        if valid_ssid == False: print self.utc_ts() + ("IO | Error: Invalid Subsystem ID: %s, from user: %s" % (self.req.ssid, self.req.userid))
       
        #Validate Device ID Field
        valid_device = False
        for i in range(len(self.device_list)): 
            if self.device_list[i] == self.req.device: valid_device = True
        if valid_device == False: print self.utc_ts() + ("IO | Error: Invalid Device ID: %s, from user: %s" % (self.req.device, self.req.userid))

        #Validate State Field
        valid_state = False
        for i in range(len(self.state_list)): 
            if self.state_list[i] == self.req.state: valid_state = True
        if valid_state == False: print self.utc_ts() + ("IO | Error: Invalid State: %s, from user: %s" % (self.req.state, self.req.userid))

        if ((valid_ssid == False) or (valid_device == False) or (valid_state == False)): return False
        else: return True

    def Process_Query(self):
        #Daemon should already know the state of all relays
        self.Read_Relay_State()
        if self.req.ssid == 'ALL':
            for i in range(len(self.relays)):
                for j in range(len(self.relays[i].ssid)):
                    self.Print_Relay(i)
                    self.Send_Query_Feedback(self.req.userid, self.relays[i].ssid[j], self.relays[i].device, str(self.relays[i].state))
        elif self.req.device == 'RF': #process RF Query for ssid
            for i in range(len(self.relays)): #cycle through relay list
                for j in range(len(self.relays[i].ssid)): #cycle through matching SSID
                    if self.relays[i].ssid[j] == self.req.ssid: #verify SSID match
                        for k in range(len(self.relays[i].group)): #cycle through group
                            if self.relays[i].group[k] == self.req.device:
                                self.Print_Relay(i)
                                self.Send_Query_Feedback(self.req.userid, self.relays[i].ssid[j], self.relays[i].device, str(self.relays[i].state))
        elif self.req.device == 'ALL': # process All Query for ssid
            for i in range(len(self.relays)):
                for j in range(len(self.relays[i].ssid)):
                    if self.relays[i].ssid[j] == self.req.ssid:
                        self.Print_Relay(i)
                        self.Send_Query_Feedback(self.req.userid, self.relays[i].ssid[j], self.relays[i].device, str(self.relays[i].state))
        else: #process query for single relay
            for i in range(len(self.relays)):
                for j in range(len(self.relays[i].ssid)):
                    if self.relays[i].ssid[j] == self.req.ssid:
                        if self.relays[i].device == self.req.device:
                            self.Print_Relay(i)
                            self.Send_Query_Feedback(self.req.userid, self.relays[i].ssid[j], self.relays[i].device, str(self.relays[i].state))

    def Send_Query_Feedback(self, userid, ssid, device, state):
        msg = userid + " " + ssid + " " + device + " " + state + "\n"
        self.sock.sendto(msg, self.addr)

    def Read_Config(self):
        path = os.getcwd() + '/' + self.config_file         
        if os.path.isfile(path) == True:
            param_f = open(path, 'r')
            param_data = param_f.read()
            param_data = param_data.strip()
            param_f.close()
            param_list = param_data.split('\n')
        #print len(param_list)
        for i in range(len(param_list)-1):
            self.relays.append(relay(param_list[i+1].split(',')))
        for i in range(8):
            self.relays[i+0].val = int(math.pow(2,i))
            self.relays[i+8].val = int(math.pow(2,i))
            self.relays[i+16].val = int(math.pow(2,i))
            self.relays[i+24].val = int(math.pow(2,i))


    def utc_ts(self):
        return str(date.utcnow()) + " UTC | "

    def stop(self):
        self.gps_ser.close()
        self._stop.set()
        sys.quit()

    def stopped(self):
        return self._stop.isSet()


