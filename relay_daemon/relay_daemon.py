#!/usr/bin/env python
#########################################
#   Title: Remote Relay Daemon          #
# Project: VTGS Relay Control Daemon    #
# Version: 2.0                          #
#    Date: Dec 15, 2017                 #
#  Author: Zach Leffke, KJ4QLP          #
# Comment:                              #
#   -Relay Control Daemon               #
#   -Intended for use with systemd      #
#########################################

import math
import string
import time
import sys
import os
import datetime
import logging

#from optparse import OptionParser
from main_thread import *
import argparse


def main():
    """ Main entry point to start the service. """

    startup_ts = datetime.datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    #--------START Command Line argument parser------------------------------------------------------
    parser = argparse.ArgumentParser(description="Relay Control Daemon")

    service = parser.add_argument_group('Daemon Service connection settings')
    service.add_argument('--ser_ip',
                         dest='ser_ip',
                         type=str,
                         default='0.0.0.0',
                         help="Service IP",
                         action="store")
    service.add_argument('--ser_port',
                         dest='ser_port',
                         type=int,
                         default='3000',
                         help="Service Port",
                         action="store")

    relay = parser.add_argument_group('Relay bank connection settings')
    relay.add_argument('--rel_ip',
                       dest='rel_ip',
                       type=str,
                       default='192.168.20.30',
                       help="Relay Bank IP",
                       action="store")
    relay.add_argument('--rel_user',
                       dest='rel_user',
                       type=str,
                       default='admin',
                       help="Relay Bank Telnet Username",
                       action="store")
    relay.add_argument('--rel_pass',
                       dest='rel_pass',
                       type=str,
                       default='admin',
                       help="Relay Bank Telnet Password",
                       action="store")

    other = parser.add_argument_group('Other daemon settings')
    other.add_argument('--ssid',
                       dest='ssid',
                       type=str,
                       default='VUL',
                       help="Subsystem ID",
                       action="store")
    other.add_argument('--log_path',
                       dest='log_path',
                       type=str,
                       default='/log/relayd',
                       help="Relay daemon logging path",
                       action="store")
    other.add_argument('--startup_ts',
                       dest='startup_ts',
                       type=str,
                       default=startup_ts,
                       help="Daemon startup timestamp",
                       action="store")

    args = parser.parse_args()
    #--------END Command Line argument parser------------------------------------------------------ 

    main_thread = Main_Thread(args)
    main_thread.daemon = True
    main_thread.run()
    sys.exit()
    

if __name__ == '__main__':
    main()
    

