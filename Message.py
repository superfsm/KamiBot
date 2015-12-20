# -*- coding: utf-8 -*-

# Copyright (C) <2015>  Shaoming Feng

# This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
# This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
# You should have received a copy of the GNU General Public License along with this program.  If not, see <http://www.gnu.org/licenses/>.

class Message():
    QQ = None
    
    from_type = -1 # 0:buddy, 1:group, 2:discu
    from_txt = ''
    from_msg_id = -1
    from_time = -1
    from_uin = -1
    from_sender = -1
    
    reply_uin = -1
    reply_txt = ''
    reply_type = -1 # 0:buddy, 1:group, 2:discu
    
    def __init__(self, QQ, result = None):
        self.QQ = QQ
        
        if QQ is None:
            return
        
        result = result[0]
        value = result['value']
        content = value['content']
        
        
        self.from_txt = content[1]
        self.from_msg_id = value['msg_id']
        self.from_time = value['time']
        
        poll_type = result['poll_type']
        if poll_type == 'message':
            self.from_type = 0
            self.from_uin = value['from_uin']
            self.from_sender = value['from_uin']
        elif poll_type == 'group_message':
            self.from_type = 1
            self.from_uin = value['from_uin']
            self.from_sender = value['send_uin']
        elif poll_type == 'discu_message':
            self.from_type = 2
            self.from_uin = value['from_uin']
            self.from_sender = value['send_uin']
        else:
            raise Exception("impossible message type")
            
        self.reply_uin = self.from_uin
        self.reply_type = self.from_type

        print '[{0}] {1} >> {2}'.format(self.from_uin, self.from_sender, self.from_txt).decode('utf-8').encode('gb2312')

    def send(self):
        self.send_txt(self.reply_txt)
        
    def send_txt(self, txt):
        self.QQ.send_msg(self.reply_type, self.reply_uin, txt)
    
    def send_txt_to(self, txt):
        self.QQ.send_msg(0, self.reply_uin, txt)
    
    def send_txt_to_type(self, to_type, to_uin, to_txt):
        print '[{0}] {1} << {2}'.format(to_type, to_uin, to_txt).decode('utf-8').encode('gb2312')
        self.QQ.send_msg(to_type, to_uin, to_txt)
        
        
        