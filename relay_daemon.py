#!/usr/bin/env python
#########################################
#   Title: Remote Relay Daemon          #
# Project: VTGS Relay Control Daemon    #
# Version: 1.0                          #
#    Date: Dec 8, 2015                  #
#  Author: Zach Leffke, KJ4QLP          #
# Comment: This is the initial version  # 
#          of the Relay Control Daemon. #
#########################################

import math
import string
import time
import sys
import csv
import os
import datetime
import telnetlib

from optparse import OptionParser
#from main_thread import *

def main:
    """ Main entry point to start the service. """
    #--------START Command Line option parser------------------------------------------------------
    usage  = "usage: %prog "
    parser = OptionParser(usage = usage)
    h_serv_ip       = "Set Service IP [default=%default]"
    h_serv_port     = "Set Service Port [default=%default]"
    h_rel_ip        = "Set Remote Relay IP [default=%default]"
    #h_rel_port      = "Set Remote Relay Port [default=%default]"
    h_user          = "Set Relay Telnet Username [default=%default]"
    h_pass          = "Set Relay Telnet Password [default=%default]"
    
    parser.add_option("", "--serv_ip"  , dest="serv_ip"  , type="string", default="0.0.0.0"      , help=h_serv_ip)
    parser.add_option("", "--serv_port", dest="serv_port", type="int"   , default="3000"         , help=h_serv_port)
    parser.add_option("", "--rel_ip"   , dest="rel_ip"   , type="string", default="192.168.20.30", help=h_rel_ip)
    #parser.add_option("", "--rel_port" , dest="rel_port" , type="int"   , default="23"           , help=h_rel_port)
    parser.add_option("", "--username" , dest="username" , type="string", default="admin"        , help=h_user)
    parser.add_option("", "--password" , dest="password" , type="string", default="admin"        , help=h_pass)
    
    (options, args) = parser.parse_args()
    #--------END Command Line option parser------------------------------------------------------    

    #serv = Main_Thread(options)
    #serv.daemon = True
    #serv.run()

    host = options.rel_ip
    username = options.username
    password = options.password

    tn = telnetlib.Telnet(host)

    tn.read_until("User Name: ")
    tn.write(username + "\n")
    print 'entered login'
    if password:
        tn.read_until("Password: ")
        tn.write(password + "\n")

    print 'Connected!'
    #while 1:
    #    pass
    sys.exit()

if __name__ == '__main__':
    main()
    

