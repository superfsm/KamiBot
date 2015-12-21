# -*- coding: utf-8 -*-

# Copyright (C) <2015>  Shaoming Feng

# This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
# This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
# You should have received a copy of the GNU General Public License along with this program.  If not, see <http://www.gnu.org/licenses/>.

import Config

class Message():
    #QQ = None

    #from_type = -1 # 0:buddy, 1:group, 2:discu
    #from_txt = ''
    #from_msg_id = -1
    #from_time = -1
    #from_uin = -1
    #from_sender = -1

    #reply_uin = -1
    #reply_txt = ''
    #reply_type = -1 # 0:buddy, 1:group, 2:discu

    def __init__(self, QQ, result = None, dummy_txt = None):
        self.QQ = QQ

        if not dummy_txt is None:
            self.from_type = 0
            self.from_txt = dummy_txt.decode(Config.console_encoding).encode('utf-8')
            self.from_msg_id = -1
            self.from_time = -1
            self.from_uin = 0
            self.from_sender = 0

            self.reply_uin = 0
            self.reply_txt = ''
            self.reply_type = 0
        else:

            if result is None:
                return

            result = result[0]
            value = result['value']
            content = value['content']

            # ignore emotion
            self.from_txt = ''
            for c in content:
                if isinstance(c,list):
                    if c[0] != 'font':
                        if not self.from_txt:
                            self.from_txt += '['+str(c[1])+']'
                        else:
                            self.from_txt += ' ['+str(c[1])+']'
                else:
                    if not self.from_txt:
                        self.from_txt += c
                    else:
                        self.from_txt += ' ' + c

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



        print '[{0:>10}] {1:>10} >> {2}'.format(self.from_uin, self.from_sender, self.from_txt).decode('utf-8').encode(Config.console_encoding,'ignore')

    def send(self):
        self.send_txt(self.reply_txt)

    def send_txt(self, txt):
        self.send_txt_to_type(self.reply_type, self.reply_uin, txt)

    def send_txt_to_type(self, to_type, to_uin, to_txt):
        print '[{0:>10}] {1:>10} << {2}'.format(to_type, to_uin, to_txt).decode('utf-8').encode(Config.console_encoding,'ignore')
        if to_uin != 0:
            self.QQ.send_msg(to_type, to_uin, to_txt)



