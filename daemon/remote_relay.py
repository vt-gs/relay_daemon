#!/usr/bin/env python
import socket
import os
import string
import sys
import time
from datetime import datetime as date
import curses
import threading
from binascii import *
from optparse import OptionParser

class remote_relay(object):
    def __init__ (self, ip, port):
        self.ip             = ip        #IP Address of MD01 Controller
        self.port           = port      #Port number of MD01 Controller
        #self.timeout        = timeout   #Socket Timeout interval, default = 1.0 seconds
        #self.retries        = retries   #Number of times to attempt reconnection, default = 2
        self.feedback       = ''        #contains received data from Relay Bank
        self.get_status_msg = "$,Q"     #Query Status Message, returns Relay State and ADC voltages
        self.get_adcs_msg   = "$,V"     #Query ADC Voltages Message
        self.adcs_fb        = [0,0,0,0,0,0,0,0] #contains feedback values of ADC Voltages
        self.get_relays_msg = "$,R"     #Query Relay State Message
        self.relays_fb      = [0,0,0,0] #Contains relay bank register values, [SPDTA, SPDTB, DPDTA, DPDTB]
        self.set_relays_msg = ''        #Set Relay State Control Message:  $,R,AAA,BBB,CCC,DDD
        self.relays_cmd     = [0,0,0,0] #Contains commanded values for formatting set_relay_msg
        self.connected      = False #TCP Connection Status

    def getTimeStampGMT(self):
        return str(date.utcnow()) + " UTC | "

    def connect(self):
        #connect to Remote Relay controller
        self.sock       = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #TCP Socket
        self.sock.settimeout(self.timeout)   #set socket timeout
        #timestamp = self.getTimeStampGMT()
        print self.getTimeStampGMT() + 'RR |  Attempting to connect to RR Controller: ' + str(self.ip) + ' ' + str(self.port)
        try:
            self.sock.connect((self.ip, self.port))
            #upon connection, get status to determine current relay positions
            self.connected = True
            print self.getTimeStampGMT() + "RR |  Successfully connected to Remote Relay Controller"
            return self.connected
            #self.get_status()
        except socket.error as msg:
            print "Exception Thrown: " + str(msg) + " (" + str(self.timeout) + "s)"
            print "Unable to connect to Remote Relay at IP: " + str(self.ip) + ", Port: " + str(self.port)  
            print "Terminating Program..."
            self.connected = False
            return self.connected

    def disconnect(self):
        #disconnect from relay controller
        print self.getTimeStampGMT() + "RR |  Attempting to disconnected from Remote Relay Controller"
        self.sock.shutdown(socket.SHUT_RDWR)
        self.sock.close()
        self.connected = False
        print self.getTimeStampGMT() + "RR |  Successfully disconnected from Remote Relay Controller"

    def set_relays(self, relays_cmd):
        self.relays_cmd = relays_cmd
        self.formatSetRelayMsg()
        if self.connected == False:
            self.printNotConnected('Set Relays')
            return -1
        else:
            try:
                print self.getTimeStampGMT() + 'RR |  Sending control message: ' + self.set_relay_msg
                self.sock.send(self.set_relay_msg) 
                time.sleep(0.250)
                self.feedback = self.sock.recv(1024)  
                print self.getTimeStampGMT() + "RR |  Received feedback message: " + self.feedback.strip()
                a = self.parse_relay_feedback(self.feedback)  
                return a
            except socket.error as msg:
                print "Exception Thrown: " + str(msg) + " (" + str(self.timeout) + "s)"
                print "Closing socket, Terminating program...."
                self.sock.close()
                self.connected = False
                return self.connected

    def formatSetRelayMsg(self):
        self.set_relay_msg = '$,R,'
        #SPDT A
        if   (len(str(self.relays_cmd[0])) == 1): self.set_relay_msg += '00' + str(self.relays_cmd[0])
        elif (len(str(self.relays_cmd[0])) == 2): self.set_relay_msg += '0'  + str(self.relays_cmd[0])
        elif (len(str(self.relays_cmd[0])) == 3): self.set_relay_msg +=        str(self.relays_cmd[0])
        self.set_relay_msg += ','
        #SPDT B
        if   (len(str(self.relays_cmd[1])) == 1): self.set_relay_msg += '00' + str(self.relays_cmd[1])
        elif (len(str(self.relays_cmd[1])) == 2): self.set_relay_msg += '0'  + str(self.relays_cmd[1])
        elif (len(str(self.relays_cmd[1])) == 3): self.set_relay_msg +=        str(self.relays_cmd[1])
        self.set_relay_msg += ','
        #DPDT A
        if   (len(str(self.relays_cmd[2])) == 1): self.set_relay_msg += '00' + str(self.relays_cmd[2])
        elif (len(str(self.relays_cmd[2])) == 2): self.set_relay_msg += '0'  + str(self.relays_cmd[2])
        elif (len(str(self.relays_cmd[2])) == 3): self.set_relay_msg +=        str(self.relays_cmd[2])
        self.set_relay_msg += ','
        #DPDT B
        if   (len(str(self.relays_cmd[3])) == 1): self.set_relay_msg += '00' + str(self.relays_cmd[3])
        elif (len(str(self.relays_cmd[3])) == 2): self.set_relay_msg += '0'  + str(self.relays_cmd[3])
        elif (len(str(self.relays_cmd[3])) == 3): self.set_relay_msg +=        str(self.relays_cmd[3])
        #print 'RR |  Sending Set Relay Message: ' + self.set_relay_msg

    def get_status(self):
        #get relay position and ADC feedback from controller
        if self.connected == False:
            self.printNotConnected('Get Relay & ADC Status')
            return -1, -1
        else:
            try:
                print self.getTimeStampGMT() + "RR |  Sending control message: " + self.get_status_msg
                self.sock.send(self.get_status_msg) 
                time.sleep(0.250)
                self.feedback = self.sock.recv(1024)  
                data_lines = self.feedback.split('\n')
                print self.getTimeStampGMT() + "RR |  Received feedback message: " + data_lines[0]
                print self.getTimeStampGMT() + "RR |  Received feedback message: " + data_lines[1]
                a = self.parse_relay_feedback(data_lines[0])
                b = self.parse_adc_feedback(data_lines[1]) 
                
                return a, b 
            except socket.error as msg:
                print "Exception Thrown: " + str(msg) + " (" + str(self.timeout) + "s)"
                print "Closing socket, Terminating program...."
                self.sock.close()
                sys.exit()

    def get_relays(self):
        #get relay position and ADC feedback from controller
        if self.connected == False:
            self.printNotConnected('Get Relay Status')
            return -1
        else:
            try:
                print self.getTimeStampGMT() + "RR |  Sending control message: " + self.get_relays_msg
                self.sock.send(self.get_relays_msg) 
                time.sleep(0.250)
                self.feedback = self.sock.recv(1024)  
                print self.getTimeStampGMT() + "RR |  Received feedback message: " + self.feedback.strip()
                a = self.parse_relay_feedback(self.feedback)  
                return a
            except socket.error as msg:
                print "Exception Thrown: " + str(msg) + " (" + str(self.timeout) + "s)"
                print "Closing socket, Terminating program...."
                self.sock.close()
                sys.exit()
        
    def get_adcs(self):
        #get relay position and ADC feedback from controller
        if self.connected == False:
            self.printNotConnected('Get ADC Status')
            return -1
        else:
            try:
                print self.getTimeStampGMT() + "RR |  Sending control message: " + self.get_adcs_msg
                self.sock.send(self.get_adcs_msg) 
                time.sleep(0.250)
                self.feedback = self.sock.recv(1024) 
                print self.getTimeStampGMT() + "RR |  Received feedback message: " + self.feedback.strip()
                b = self.parse_adc_feedback(self.feedback)  
                return b
            except socket.error as msg:
                print "Exception Thrown: " + str(msg) + " (" + str(self.timeout) + "s)"
                print "Closing socket, Terminating program...."
                self.sock.close()
                sys.exit()
        
    def parse_relay_feedback(self, data_line):
        data = data_line.split(',')
        if (data[0] == '$') and (data[1] == 'R'): #Valid Relay Feedback Message
            for i in range(4):
                self.relays_fb[i] = int(data[i+2].strip())
                #print bin(self.relays_fb[i])
            #print self.relays_fb
        return self.relays_fb

    def parse_adc_feedback(self, data_line):
        data = data_line.split(',')
        if (data[0] == '$') and (data[1] == 'V'): #Valid ADC Feedback Message
            for i in range(8): self.adcs_fb[i] = float(data[i+2].strip())
            #print self.adcs_fb
        return self.adcs_fb

    def utc_ts(self):
        return str(date.utcnow()) + " UTC | "

    def printNotConnected(self, msg):
        print self.getTimeStampGMT() + "RR |  Cannot " + msg + " until connected to Remote Relay Controller."

    def set_ipaddr(self, ip):
        self.ip = ip
        print self.getTimeStampGMT() + "RR |  Updated RR Controller IP Address to: " + self.ip

    def set_port(self, port):
        self.port = int(port)
        print self.getTimeStampGMT() + "RR |  Updated RR Controller TCP Port: " + str(self.port)



