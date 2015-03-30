#!/usr/bin/env python
import socket
import os
import string
import sys
import time
import threading

class Data_Server(threading.Thread):
    def __init__ (self, options):
        threading.Thread.__init__(self)
        self._stop = threading.Event()
        self.ip = options.ip
        self.port = options.port
        self.suspend = False
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) #UDP Socket
        self.packet_list = []
        self.rtt_tlm = rtt_tlm()

    def run(self):
        self.sock.bind((self.ip, self.port))
        while (not self._stop.isSet()):
            if self.suspend == False: 
                data = self.sock.recv(1024)
                if len(data) == 256:
                    self.packet_list.append(data)
                    self.Decode_Packet(data)
                #print len(data)
                #for i in range(len(data)):
                #    print hex(ord(data[i]))
        sys.exit()

    def Decode_Packet(self, data):
        self.gui.raw_textbox.insertPlainText(str(binascii.hexlify(data)) + '\n\n')

    def set_gui_access(self, gui_handle):
        self.gui = gui_handle

    def stop(self):
        self._stop.set()

    def stopped(self):
        return self._stop.isSet()
