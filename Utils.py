# -*- coding: utf-8 -*-

# Copyright (C) <2015>  Shaoming Feng

# This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
# This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
# You should have received a copy of the GNU General Public License along with this program.  If not, see <http://www.gnu.org/licenses/>.

import logging

import Config

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
