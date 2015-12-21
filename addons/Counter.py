# -*- coding: utf-8 -*-

# Copyright (C) <2015>  Shaoming Feng

# This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
# This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
# You should have received a copy of the GNU General Public License along with this program.  If not, see <http://www.gnu.org/licenses/>.

import pickle

from AbstractHandler import *
import Config

_COUNTER_PATH = 'saved/counter.pickle'


#Counte the number of reloads of the modules
class Handler(AbstractHandler):
    
    def init(self):
        
        try:
            with open(_COUNTER_PATH, 'rb') as handle:
                self.counter = pickle.load(handle)
        except:
            self.counter = 0
            
        self.counter += 1
        
        try:
            with open(_COUNTER_PATH, 'wb') as handle:
                pickle.dump(self.counter, handle)
        except:
            print "***CANNOT DUMP"

    def process(self, msg):
        
        sender = self.QQ.get_friend_uin(msg.from_sender)
        if not sender in Config.group_root:
            return False

        txt = msg.from_txt

        reply = ''
        if txt in ('##!info', '##！info'):
            return True, '这是{!s}在记事以来，在主人调教下的的第{!s}号人格！'.format(Config.name_bot, self.counter)
        return False
