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

from optparse import OptionParser
from main_thread import *

if __name__ == '__main__':
    #--------START Command Line option parser------------------------------------------------------
    usage  = "usage: %prog "
    parser = OptionParser(usage = usage)
    h_serv_ip       = "Set Service IP [default=%default]"
    h_serv_port     = "Set Service Port [default=%default]"
    h_rel_ip        = "Set Remote Relay IP [default=%default]"
    h_rel_port      = "Set Remote Relay Port [default=%default]"
    
    parser.add_option("", "--serv_ip"  , dest="serv_ip"  , type="string", default="127.0.0.1" , help=h_serv_ip)
    parser.add_option("", "--serv_port", dest="serv_port", type="int"   , default="3000"      , help=h_serv_port)
    parser.add_option("", "--rel_ip"  , dest="rel_ip"  , type="string", default="192.168.42.11" , help=h_rel_ip)
    parser.add_option("", "--rel_port", dest="rel_port", type="int"   , default="2000"          , help=h_rel_port)
    
    (options, args) = parser.parse_args()
    #--------END Command Line option parser------------------------------------------------------    

    serv = Main_Thread(options)
    serv.daemon = True
    serv.run()

    while 1:
        pass
    sys.exit()
    

