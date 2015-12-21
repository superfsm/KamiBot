# -*- coding: utf-8 -*-

# Copyright (C) <2015>  Shaoming Feng

# This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
# This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
# You should have received a copy of the GNU General Public License along with this program.  If not, see <http://www.gnu.org/licenses/>.

import time
import random

from AbstractHandler import *
import Config

_NAME = [
    '小忍',
    'Shinobu',
    '萝莉',
    '吸血鬼',
    '怪异之王',
    '忍野',
    '刃下心',
    'Oshino'
]

class Handler(AbstractHandler):

    def process(self, msg):
        
        txt = msg.from_txt
        
        isHost = False
        sender = self.QQ.get_friend_uin(msg.from_sender)
        if sender in Config.group_root:
            isHost = True
            
        hour = time.localtime(time.time()).tm_hour
        if hour > 7 and hour < 18:
            isDay = True
        else:
            isDay = False
        
        if self.isName(txt) or (self.containsName(txt) and len(txt) <= 4):
            if isHost:
                if isDay:
                    return True, random.choice(['虽然是白天，看在主人的面之上我还是出来了呢','Kamisama~~要带我出去玩嘛，虽然是白天的啦，不过要是有甜甜圈的话','咔咔，吾主哦，呼唤吾有何事','吾之半身，何事？'])
                else:
                    return True, random.choice(['咔咔，吾主哦，呼唤吾有何事','Kamisama~~要带我出去玩嘛？','不是说好了先吃饭的吗？','嗯哼哼，主人你终于想起来我了','吾之半身，何事？','你这个萝莉控，3000￥！','给吾甜甜圈，吾给予汝前发娘的胖次'])
            else:
                if isDay:
                    return True, random.choice(['大白天的吵什么，晚上再说','嗯？zzzzzz','Mr.Donut拿来！作为呼唤吾的代价','只要甜甜圈存在之一天，吾就不会毁灭人类!','纳尼？','要成为吾的眷属么？'])
                else:
                    return True, random.choice(['哦，是要和我去玩吗？','只要甜甜圈存在之一天，吾就不会毁灭人类!','纳尼？','嗯？已经这个时候了么','&^%#(*$#,等我吃完的','好想吸血啊，给我吃一点好不好，就一点点','要成为吾的眷属么？'])
                    
        if txt.find('甜甜圈') > -1:
            return True,  random.choice(['在哪里在哪里？！快带我去','不要诱骗小萝莉！！哦不，等等~','好像听到了什么愉悦的东西','只要甜甜圈存在之一天，吾就不会毁灭人类!'])
        
        return False
        
    def isName(self, txt):
        if txt in _NAME:
            return True
        return False
        
    def containsName(self,txt):
        for n in _NAME:
            if txt.find(n) > -1:
                return True
        return False
        
