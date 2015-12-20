#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) <2015>  Shaoming Feng

# This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
# This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
# You should have received a copy of the GNU General Public License along with this program.  If not, see <http://www.gnu.org/licenses/>.

import sys
reload(sys)
sys.setdefaultencoding("utf-8")
sys.dont_write_bytecode = True

import argparse
import time

from QQ import *
from Message import *

def init_logging(debug = False):
    
    rootLogger = logging.getLogger()
    rootLogger.setLevel(logging.DEBUG)

    logFormatter = logging.Formatter('%(asctime)s  %(filename)-20s[line:%(lineno)-3d] %(levelname)5s %(message)s', datefmt='%a, %d %b %Y %H:%M:%S')
    fileHandler = logging.FileHandler('qq.log')
    fileHandler.setFormatter(logFormatter)
    fileHandler.setLevel(logging.DEBUG)
    rootLogger.addHandler(fileHandler)

    logFormatter = logging.Formatter('%(filename)-20s[line:%(lineno)-3d] %(levelname)5s %(message)s', datefmt='%a, %d %b %Y %H:%M:%S')
    consoleHandler = logging.StreamHandler()
    consoleHandler.setFormatter(logFormatter)
    if debug:
        consoleHandler.setLevel(logging.DEBUG)
    else:
        consoleHandler.setLevel(logging.ERROR)
    rootLogger.addHandler(consoleHandler)
    
    #Test
    logging.debug('logging system set')

if __name__ == '__main__':
        
    #Parse arguments
    parser = argparse.ArgumentParser()
    parser.set_defaults(debug=False)
    parser.add_argument('-d', dest='debug', action='store_true')
    args = parser.parse_args()
    
    #Initialize Logging
    init_logging(args.debug)
    
    #Start Client
    client = QQ()
    if client.QR_login():
        client.start()
    else:
        logging.error('Quit QQ starting failed')
        
    while True:
        dummy_txt = raw_input("Dummy Message >>").strip()
        if dummy_txt.strip() == '':
            continue
        client.msgQ.put(Message(client, dummy_txt = dummy_txt))
        time.sleep(0.1)
        while not client.msgQ.empty():
            time.sleep(0.1)
        
        
        
        
        
