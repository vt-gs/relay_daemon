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
#from curses_display import *


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
    relay.connect()

    while True:
        x = raw_input('Send command: r=Set Relay, v=Query Voltage, q=Query All, e=Exit: ')
        if (x == 'r'):  
            pass
        elif (x == 'v'):  
            pass
            print cur_az, cur_el
        elif (x == 'q'):
            target_az = raw_input('  Enter Azimuth: ')
            target_el = raw_input('Enter Elevation: ')
            target_az = float(target_az)
            target_el = float(target_el)
            relay.set_position(target_az, target_el)            
        elif (x == 'e'):
            print "Received \'Quit\' Command"
            print "Closing Socket, Terminating Program..."
            relay.disconnect()
            sys.exit()
    
    sys.exit()

