# -*- coding: utf-8 -*-

# Copyright (C) <2015>  Shaoming Feng

# This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
# This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
# You should have received a copy of the GNU General Public License along with this program.  If not, see <http://www.gnu.org/licenses/>.
import jieba
import codecs
from collections import defaultdict
import random
import os

from addons.AbstractHandler import *
import Config

_STOPWORDS = ('~!@#$%^&*()-_=+[{]};:\'",<.>/?·~！@#￥%……&*（）-——=+【{】}；：‘“，《。》、？')
_DEBUG = Config.debug
_CQNAME = Config.name_bot

class Handler(AbstractHandler):

    def init(self):
        jieba.initialize()
        self._init_dict()

    def _init_dict(self):
        self.H = defaultdict(set)
        
        mypath = os.path.dirname(__file__)
        mypath = os.path.join(mypath, 'dicts/')
        files = [os.path.join(mypath, f) for f in os.listdir(mypath) if os.path.isfile(os.path.join(mypath, f))]

        for f in files:
            
            if Config.debug:
                print '----------'
                print 'Find dict ' + f + '...'

            with codecs.open(f,'r','gb2312','ignore') as f:
                lines = f.readlines()
                i = 1
                while i < len(lines):
                    self.H[lines[i-1].strip()].add(lines[i].strip())
                    i += 3

    def process(self, msg):

        #if not self.QQ.get_friend_uin(msg.from_sender) in Config.group_root:
        #    return True, ''

        seg_list = list(jieba.cut(msg.from_txt, cut_all=True))
        seg_list = [x for x in seg_list if (x not in _STOPWORDS)]
        seg_list.sort(key=len, reverse=True)


        debug_txt = "/".join(seg_list)

        for i in seg_list:
            if i in self.H:
                debug_txt += ' [' + i + ']'
                if _DEBUG:
                    print '----------'
                    print debug_txt
                    for j in self.H[i]:
                        print j.encode(Config.console_encoding, 'ignore')
                return True, self.replace(random.choice(list(self.H[i])))
        if _DEBUG:
            print debug_txt
        return True, ''

    def replace(self, txt):
        return txt.replace('[cqname]', _CQNAME).replace('[name]', '你')

