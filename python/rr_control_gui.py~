#!/usr/bin/env python
import socket
import os
import string
import sys
import time
import curses
import threading
from optparse import OptionParser
from binascii import *
from remote_relay import *
from rr_main_gui import *
#from curses_display import *


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

if __name__ == '__main__':
	
    #--------START Command Line option parser------------------------------------------------
    usage = "usage: %prog -a <Server Address> -p <Server Port> "
    parser = OptionParser(usage = usage)
    s_help = "IP address of Relay Bank, Default: 192.168.42.11"
    p_help = "TCP port number of Relay Bank, Default: 2000"
    parser.add_option("-a", dest = "ip"  , action = "store", type = "string", default = "192.168.42.11", help = s_help)
    parser.add_option("-p", dest = "port", action = "store", type = "int"   , default = "2000"         , help = p_help)
    (options, args) = parser.parse_args()
    #--------END Command Line option parser-------------------------------------------------
    
    #relay = remote_relay(options.ip, options.port)
    #relay.connect()

    #server_thread = Data_Server(options)
    #server_thread.daemon = True
    #server_thread.start()

    app = QtGui.QApplication(sys.argv)
    win = MainWindow()
    win.show()
    #server_thread.set_gui_access(ex)
    sys.exit(app.exec_())

    
    
    sys.exit()

