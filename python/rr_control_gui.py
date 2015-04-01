#!/usr/bin/env python
import socket
import os
import string
import sys
import time
from optparse import OptionParser
from binascii import *
from rr_main_gui import *
from data_thread_rr import *


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
    
    relay = remote_relay(options.ip, options.port)
    #relay.connect()

    #relay_thread = Data_Thread(options)
    #relay_thread.daemon = True
    #relay_thread.start()

    app = QtGui.QApplication(sys.argv)
    win = MainWindow()
    win.setCallback(relay)
    win.show()
    #server_thread.set_gui_access(ex)
    sys.exit(app.exec_())

    
    
    sys.exit()

