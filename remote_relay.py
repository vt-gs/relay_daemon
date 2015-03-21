#!/usr/bin/env python
import socket
import os
import string
import sys
import time
import curses
import threading
from binascii import *
from optparse import OptionParser

class remote_relay(object):
    def __init__ (self, ip, port, timeout = 1.0, retries = 2):
        self.ip         = ip        #IP Address of MD01 Controller
        self.port       = port      #Port number of MD01 Controller
        self.sock       = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #TCP Socket
        self.timeout    = timeout   #Socket Timeout interval, default = 1.0 seconds
        self.sock.settimeout(timeout)   #set socket timeout
        self.retries    = retries   #Number of times to attempt reconnection, default = 2
        self.feedback   = ''        #contains received data from Relay Bank
        self.relays     = [0,0,0,0]
        self.adcs       = [0,0,0,0,0,0,0,0]
        self.spdta      = 0 #byte containing state information for SPDT Relay Bank A (1-8)
        self.spdtb      = 0 #byte containing state information for SPDT Relay Bank B (9-16)
        self.dpdta      = 0 #byte containing state information for DPDT Relay Bank A (1-8)
        self.dpdtb      = 0 #byte containing state information for DPDT Relay Bank B (9-16)
        self.status_cmd = "$,Q"
        self.adc_cmd    = "$,V"
        self.relay_cmd  = "$,R"

    def connect(self):
        #connect to Remote Relay controller
        try:
            self.sock.connect((self.ip, self.port))
            #upon connection, get status to determine current relay positions
            self.get_status()
        except socket.error as msg:
            print "Exception Thrown: " + str(msg) + " (" + str(self.timeout) + "s)"
            print "Unable to connect to Remote Relay at IP: " + str(self.ip) + ", Port: " + str(self.port)  
            print "Terminating Program..."
            sys.exit()

    def disconnect(self):
        #disconnect from relay controller
        self.sock.close()
    
    def get_status(self):
        #get relay position and ADC feedback from controller
        try:
            self.sock.send(self.status_cmd) 
            time.sleep(0.250)
            self.feedback = self.sock.recv(1024)    
        except socket.error as msg:
            print "Exception Thrown: " + str(msg) + " (" + str(self.timeout) + "s)"
            print "Closing socket, Terminating program...."
            self.sock.close()
            sys.exit()
        self.parse_status_feedback()  

    def get_relays(self):
        #get relay position and ADC feedback from controller
        try:
            self.sock.send('$,R') 
            time.sleep(0.250)
            self.feedback = self.sock.recv(1024)    
        except socket.error as msg:
            print "Exception Thrown: " + str(msg) + " (" + str(self.timeout) + "s)"
            print "Closing socket, Terminating program...."
            self.sock.close()
            sys.exit()
        self.parse_relay_feedback(self.feedback)  

    def get_adcs(self):
        #get relay position and ADC feedback from controller
        try:
            self.sock.send('$,V') 
            time.sleep(0.250)
            self.feedback = self.sock.recv(1024)    
        except socket.error as msg:
            print "Exception Thrown: " + str(msg) + " (" + str(self.timeout) + "s)"
            print "Closing socket, Terminating program...."
            self.sock.close()
            sys.exit()
        self.parse_relay_feedback(self.feedback)  

    def parse_status_feedback(self):
        #$,R,spdta,sptdb,dpdta,dpdtb
        #$,V,adc1,adc2,adc3,adc4,adc5,adc6,adc7,adc8
        data_lines = self.feedback.split('\n')
        self.parse_relay_feedback(data_lines[0])
        self.parse_adc_feedback(data_lines[1])

    def parse_relay_feedback(self, data_line):
        data = data_line.split(',')
        if (data[0] == '$') and (data[1] == 'R'): #Valid Relay Feedback Message
            for i in range(4):
                self.relays[i] = int(data[i+2].strip())
                print bin(self.relays[i])
            print self.relays

    def parse_adc_feedback(self, data_line):
        data = data_line.split(',')
        if (data[0] == '$') and (data[1] == 'V'): #Valid ADC Feedback Message
            for i in range(8): self.adcs[i] = float(data[i+2].strip())
            print self.adcs

    




class Tracker_Thread(threading.Thread):
    def __init__ (self, options):
        threading.Thread.__init__(self)
        self._stop = threading.Event()
        self.ip = options.ip
        self.port = options.port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #TCP Socket
        self.cmd_az = 0.0       #Commanded Azimuth
        self.cmd_el = 0.0       #Commanded Elevation
        self.current_az = 0.0   #Current Azimuth
        self.current_el = 0.0   #Current Elevation
        self.az_tol = 0.0       #Azimuth Tolerance
        self.el_tol = 0.0       #Elevation Tolerance
        self.status = ""        #Antenna Pedestal Status

    def run(self):
        self.sock.connect((self.ip,self.port))
        while (not self._stop.isSet()):
            #data = self.sock.recv(1024)
            data = self.sock.makefile().readline(1024)
            data = data.strip('\n')
            data_list = data.split(',')
            if data_list[0] == '$':
                self.cmd_az     = float(data_list[1])   #Commanded Azimuth
                self.cmd_el     = float(data_list[2])   #Commanded Elevation
                self.current_az = float(data_list[3])   #Current Azimuth
                self.current_el = float(data_list[4])   #Current Elevation
                self.az_tol     = float(data_list[5])   #Azimuth Tolerance
                self.el_tol     = float(data_list[6])   #Elevation Tolerance
                self.status     = data_list[7].strip('\r')        #Antenna Pedestal Status
            #print self.cmd_az, self.cmd_el, self.current_az, self.current_el, self.az_tol, self.el_tol, self.status
        sys.exit()
        #time.sleep(0.25)

    
    def Write_Message(self, az, el):
        az_str = str(int(az))
        el_str = str(int(el))

        if len(az_str) == 1:
            az_str = "00" + az_str
        elif len(az_str) == 2:
            az_str = "0" + az_str
        
        if len(el_str) == 1:
            el_str = "00" + el_str
        elif len(el_str) == 2:
            el_str = "0" + el_str

        msg = "W" + az_str + " " + el_str
        #print msg
        self.sock.send(msg)

    def Write_Raw_Message(self, cmd):
        self.sock.send(cmd)

    def get_feedback(self):
        return self.cmd_az, self.cmd_el, self.current_az, self.current_el, self.az_tol, self.el_tol, self.status

    def stop(self):
        self._stop.set()

    def stopped(self):
        return self._stop.isSet()
