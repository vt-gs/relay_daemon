#!/usr/bin/env python
#############################################################
#   Title: Remote Relay Daemon  Client                      #
# Project: VTGS Relay Control Daemon                        #
# Version: 2.0                                              #
#    Date: Feb 12, 2017                                     #
#  Author: Zach Leffke, KJ4QLP                              #
# Comment:                                                  #
#   -Relay Control Daemon Client                            #
#   -Simple client program to exercise                      #
#      RabbitMQ interface to daemon                         #
#   -Config File NOTE:                                      #
#       The produce/consume keys in the config file are     #
#       flipped as the client will be producing commands    #
#       and consuming feedback.                             #
#       IMPORTANT:  The 'relays' fields match               #
#############################################################

import math
import string
import time
import sys
import os
import datetime
import logging
import json

#from optparse import OptionParser
from main_thread import *
import argparse

def main():
    """ Main entry point to start the service. """

    startup_ts = datetime.datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    #--------START Command Line argument parser------------------------------------------------------
    parser = argparse.ArgumentParser(description="Relay Control Daemon")

    cfg = parser.add_argument_group('Daemon Configuration File')
    cfg.add_argument('--cfg_path',
                       dest='cfg_path',
                       type=str,
                       default=os.getcwd(),
                       help="Daemon Configuration File Path",
                       action="store")
    cfg.add_argument('--cfg_file',
                       dest='cfg_file',
                       type=str,
                       default="relay_config_vu.json",
                       help="Daemon Configuration File",
                       action="store")

    args = parser.parse_args()
    #--------END Command Line argument parser------------------------------------------------------

    fp_cfg = '/'.join([args.cfg_path,args.cfg_file])
    print fp_cfg
    if not os.path.isfile(fp_cfg) == True:
        print 'ERROR: Invalid Configuration File: {:s}'.format(fp_cfg)
        sys.exit()
    print 'Importing configuration File: {:s}'.format(fp_cfg)
    with open(fp_cfg, 'r') as json_data:
        cfg = json.load(json_data)
        json_data.close()
    cfg['startup_ts'] = startup_ts
    #print cfg

    main_thread = Main_Thread(cfg)
    main_thread.daemon = True
    main_thread.run()
    sys.exit()


if __name__ == '__main__':
    main()
