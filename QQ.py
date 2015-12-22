# -*- coding: utf-8 -*-

# Copyright (C) <2015>  Shaoming Feng

# This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
# This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
# You should have received a copy of the GNU General Public License along with this program.  If not, see <http://www.gnu.org/licenses/>.

import random
import time
import datetime
import re
import json
import logging
import thread
import os
import js2py
from Queue import Queue
from PIL import Image

from HttpClient import *
from Message import *
from Dispatcher import *

_SMART_QQ_URL = 'http://w.qq.com/login.html'
_QR_PATH = './QR.jpg'
_REFERER_URL = 'http://d1.web2.qq.com/proxy.html?v=20151105001&callback=1&id=2'
_REFERER_URL_2013 = 'http://s.web2.qq.com/proxy.html?v=20130916001&callback=1&id=1'

_HASH_JS = """
        u = function(x, I) {
            x += "";
            for (var N = [], T = 0; T < I.length; T++) N[T % 4] ^= I.charCodeAt(T);
            var U = ["EC", "OK"],
                V = [];
            V[0] = x >> 24 & 255 ^ U[0].charCodeAt(0);
            V[1] = x >> 16 & 255 ^ U[0].charCodeAt(1);
            V[2] = x >> 8 & 255 ^ U[1].charCodeAt(0);
            V[3] = x & 255 ^ U[1].charCodeAt(1);
            U = [];
            for (T = 0; T < 8; T++) U[T] = T % 2 == 0 ? N[T >> 1] : V[T >> 1];
            N = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "A", "B", "C", "D", "E", "F"];
            V = "";
            for (T = 0; T < U.length; T++) {
                V += N[U[T] >> 4 & 15];
                V += N[U[T] & 15]
            }
            return V
        }
        """

def _get_revalue(html, rex, er, ex):
    v = re.search(rex, html)
    if v is None:
        if ex:
            logging.error(er)
            raise TypeError(er)
        else:
            logging.warning(er)
        return ''
    return v.group(1)


def _date_to_millis():
    return int(time.mktime(datetime.datetime.utcnow().timetuple())) * 1000

def _dump_json(j):
    return json.dumps(j, sort_keys=True,indent=4, separators=(',', ': '))

class QQ:

    def __init__(self):

        # hash
        self.hash_func = js2py.eval_js(_HASH_JS)
        self.hash_value = ''

        # Http client
        self.recv_client = HttpClient()
        self.send_client = None

        # Session Info
        self.client_id = 53999199
        self.ptwebqq = ''
        self.psessionid = ''
        self.vfwebqq = ''
        self.uin = -1


        # Message Handling
        self.msgQ = Queue()
        self.msg_id = random.randint(0, 90000000)

        # Cache
        self.username = ''
        self.uin2acc = dict()
        
        # Cshard data for addons
        self.shared_data = dict()
        
    def _display_QRCode(self):
        img = Image.open(_QR_PATH)
        img.show()

    def QR_login(self):
        logging.info('Connecting to QQ server...')
        print 'Connecting to QQ server...'

        # For naming convinience
        http_client = self.recv_client


        # Get initial url
        html = http_client.GET(_SMART_QQ_URL)

        # Browse returned URL
        init_url = _get_revalue(html, r'\.src = "(.+?)"', "Get Login Url Error.", 1)
        html = http_client.GET(init_url + '0')
        star_time = _date_to_millis()

        # Get parameters
        appid = _get_revalue(html, r'<input type="hidden" name="aid" value="(\d+)" />', 'Get AppId Error', 1)
        sign = _get_revalue(html, r'g_login_sig=encodeURIComponent\("(.*?)"\)', 'Get Login Sign Error', 0)
        js_ver = _get_revalue(html, r'g_pt_version=encodeURIComponent\("(\d+)"\)', 'Get g_pt_version Error', 1)
        mibao_css = _get_revalue(html, r'g_mibao_css=encodeURIComponent\("(.+?)"\)', 'Get g_mibao_css Error', 1)

        logging.debug('appid = %s',appid)
        logging.debug('sign = %s',sign)
        logging.debug('js_ver = %s',js_ver)
        logging.debug('mibao_css = %s',mibao_css)

        # Download and check QR code
        retry = 0
        ret = []
        while True:
            retry += 1
            logging.debug('Downloading QR code')
            if os.path.exists(_QR_PATH):
                os.remove(_QR_PATH)
            http_client.download('https://ssl.ptlogin2.qq.com/ptqrshow?appid={0}&e=0&l=L&s=8&d=72&v=4'.format(appid),_QR_PATH)
            print "Please (re)scan the QR code ({0})".format(_QR_PATH)
            thread.start_new_thread(self._display_QRCode,())

            while True:
                ret = []
                html = http_client.GET('https://ssl.ptlogin2.qq.com/ptqrlogin?webqq_type=10&remember_uin=1&login2qq=1&aid={0}&u1=http%3A%2F%2Fw.qq.com%2Fproxy.html%3Flogin2qq%3D1%26webqq_type%3D10&ptredirect=0&ptlang=2052&daid=164&from_ui=1&pttype=1&dumy=&fp=loginerroralert&action=0-0-{1}&mibao_css={2}&t=undefined&g=1&js_type=0&js_ver={3}&login_sig={4}&pt_randsalt=0'.format(
                    appid, _date_to_millis() - star_time, mibao_css, js_ver, sign),init_url)
                ret = html.split("'") # 65: QRCode 失效, 0: 验证成功, 66: 未失效, 67: 验证中
                if ret[1] in ('66', '67'):
                    time.sleep(2)
                if ret[1] in ('0', '65'):
                    break

            if ret[1] == '0':
                self.ptwebqq = http_client.getCookie('ptwebqq')
                self.send_client = http_client.copy()
                break
            elif retry < 3:
                logging.warning("Re-download [%d]", retry)
                ret = []
            else:
                logging.error("QR code scanning failed")
                return False

        # Remove QR image file
        if os.path.exists(_QR_PATH):
            os.remove(_QR_PATH)

        print "Please wait..."

        # Get user nickname
        self.username = ret[11]

        # Browse proxy urls to get correct cookies
        http_client.GET(ret[5])
        http_client.GET('http://web2.qq.com/web2_cookie_proxy.html')

        # Login
        ret = {}

        html = http_client.POST('http://d1.web2.qq.com/channel/login2',
            {'r': '{{"ptwebqq":"{0}","clientid":{1},"psessionid":"{2}","status":"online"}}'.format(self.ptwebqq, self.client_id, self.psessionid)},
            _REFERER_URL)
        ret = json.loads(html)

        if ret['retcode'] != 0:
            logging.error("login return code: %s", str(ret['retcode']))
            return False

        self.psessionid = ret['result']['psessionid']
        self.uin = ret['result']['uin']

        # get hash
        logging.debug("uin = {0}".format(self.uin))
        logging.debug("ptwebqq = {0}".format(self.ptwebqq))
        self.hash_value = self.hash_func(self.uin, self.ptwebqq)
        logging.debug("hash_value = {0}".format(self.hash_value))

        # get vfwebqq
        ret = {}
        html = http_client.GET('http://s.web2.qq.com/api/getvfwebqq?ptwebqq={0}&clientid={1}&psessionid=&t={2}'.format(
            self.ptwebqq, self.client_id, _date_to_millis()), _REFERER_URL_2013)
        ret = json.loads(html)

        if ret['retcode'] != 0:
            logging.error("getvfwebqq return code: %s", str(ret['retcode']))
            return False
        self.vfwebqq = ret['result']['vfwebqq']

        # Success
        logging.info("QQ: {0} login successfully, Username：{1}".format(self.uin, self.username))
        print "Welcome, " + self.username.decode('utf-8').encode('gb2312') + "!"
        print "-------------------------------------------------------"

        # all available API's other then send_message
        # self.get_friend_uin(858401881)
        # self.get_self_info()
        # self.get_user_friends()
        # self.get_group_name_list_mask()
        # self.get_discus_list()
        # self.get_online_buddies()
        # self.get_discu_info(1899418441)
        # self.get_recent_list()
        # self.change_status('away')
        # self.get_friend_info(1582813192)
        # self.get_single_long_nick(1582813192)
        # self.get_group_info_ext(3229000491)
        return True
        
    def relogin(self):
        
        http_client = self.recv_client
        
        # Browse proxy urls to get correct cookies
        http_client.GET(ret[5])
        http_client.GET('http://web2.qq.com/web2_cookie_proxy.html')

        # Login
        ret = {}

        html = http_client.POST('http://d1.web2.qq.com/channel/login2',
            {'r': '{{"ptwebqq":"{0}","clientid":{1},"psessionid":"{2}","status":"online"}}'.format(self.ptwebqq, self.client_id, self.psessionid)},
            _REFERER_URL)
        ret = json.loads(html)

        if ret['retcode'] != 0:
            logging.error("login return code: %s", str(ret['retcode']))
            return False

        self.psessionid = ret['result']['psessionid']
        self.uin = ret['result']['uin']

        # get hash
        logging.debug("uin = {0}".format(self.uin))
        logging.debug("ptwebqq = {0}".format(self.ptwebqq))
        self.hash_value = self.hash_func(self.uin, self.ptwebqq)
        logging.debug("hash_value = {0}".format(self.hash_value))

        # get vfwebqq
        ret = {}
        html = http_client.GET('http://s.web2.qq.com/api/getvfwebqq?ptwebqq={0}&clientid={1}&psessionid=&t={2}'.format(
            self.ptwebqq, self.client_id, _date_to_millis()), _REFERER_URL_2013)
        ret = json.loads(html)

        if ret['retcode'] != 0:
            logging.error("getvfwebqq return code: %s", str(ret['retcode']))
            return False
        self.vfwebqq = ret['result']['vfwebqq']

        # Success
        logging.info("QQ: {0} login successfully, Username：{1}".format(self.uin, self.username))
        print "Welcome, " + self.username.decode('utf-8').encode('gb2312') + "!"
        print "-------------------------------------------------------"
        
        thread.start_new_thread(self._poll_loop,())
        logging.debug("Pooling thread started")

        return True

    def start(self):
        thread.start_new_thread(self._dispatch,())
        logging.debug("Dispatcher thread started")

        thread.start_new_thread(self._poll_loop,())
        logging.debug("Pooling thread started")

    def _dispatch(self):
        dispatcher = Dispatcher(self)
        dispatcher.start()

    def _poll_loop(self):
        while True:
            self._poll()

    def _poll(self, error_times=0):

        if error_times >= 5:
            if not self.relogin():
                raise IOError("Account offline.")
            else:
                error_times = 0

        # poll
        html = self.recv_client.POST('http://d1.web2.qq.com/channel/poll2', {
            'r': '{{"ptwebqq":"{1}","clientid":{2},"psessionid":"{0}","key":""}}'.format(self.psessionid,
                                                                                         self.ptwebqq,
                                                                                         self.client_id)
        }, _REFERER_URL)

        ret = json.loads(html)
        logging.debug(_dump_json(ret))

        retcode = ret['retcode']

        if retcode == 0:
            if 'errmsg' in ret:
                return
            else:
                self.msgQ.put(Message(self, ret['result']))
        else:
            time.sleep(1)
            return
            #raise Exception('A new return code caught')

    def send_msg(self, to_type, to_uin, to_txt):

        to_txt = str(to_txt.replace("\\", "\\\\\\\\").replace("\n", "\\\\n").replace("\t", "\\\\t")).decode("utf-8")

        msg_id = self.msg_id
        self.msg_id += 1

        req_url = None
        data = None
        
        if to_type == 0:
            req_url = "http://d1.web2.qq.com/channel/send_buddy_msg2"
            data = (
                ('r',
                 '{{"to":{0},"content":"[\\"{4}\\",[\\"font\\",{{\\"name\\":\\"Arial\\",\\"size\\":\\"10\\",\\"style\\":[0,0,0],\\"color\\":\\"000000\\"}}]]","face":564,"clientid":{1},"msg_id":{2},"psessionid":"{3}"}}'.format(
                     to_uin, self.client_id, msg_id, self.psessionid, to_txt)),
                ('clientid', self.client_id),
                ('psessionid', self.psessionid)
            )
        elif to_type == 1:
            req_url = "http://d1.web2.qq.com/channel/send_qun_msg2"
            data = (
                ('r',
                 '{{"group_uin":{0},"content":"[\\"{4}\\",[\\"font\\",{{\\"name\\":\\"Arial\\",\\"size\\":\\"10\\",\\"style\\":[0,0,0],\\"color\\":\\"000000\\"}}]]","face":534,"clientid":{1},"msg_id":{2},"psessionid":"{3}"}}'.format(
                     to_uin, self.client_id, msg_id, self.psessionid, to_txt)),
                ('clientid', self.client_id),
                ('psessionid', self.psessionid)
            )
        elif to_type == 2:
            req_url = "http://d1.web2.qq.com/channel/send_discu_msg2"
            data = (
                ('r',
                 '{{"did":{0},"content":"[\\"{4}\\",[\\"font\\",{{\\"name\\":\\"Arial\\",\\"size\\":\\"10\\",\\"style\\":[0,0,0],\\"color\\":\\"000000\\"}}]]","face":534,"clientid":{1},"msg_id":{2},"psessionid":"{3}"}}'.format(
                     to_uin, self.client_id, msg_id, self.psessionid, to_txt)),
                ('clientid', self.client_id),
                ('psessionid', self.psessionid)
            )

        try:
            html = self.send_client.copy().POST(req_url, data, _REFERER_URL)
            ret = json.loads(html)
            if ret['errCode'] != 0 or ret['msg'] != 'send ok':
                raise Exception("send message with error: " + ret['msg'])
        except:
            logging.exception("send_msg failed")
            return False
        return True

    def get_self_info(self):
        html = self.send_client.copy().GET(
            'http://s.web2.qq.com/api/get_self_info2?t={0}'.format(_date_to_millis()),
            _REFERER_URL_2013)
        ret = json.loads(html)
        if ret['retcode'] != 0:
            raise Exception('get_self_info error')

    def get_friend_uin(self, tuin):
        if tuin in self.uin2acc:
            return self.uin2acc[tuin]

        html = self.send_client.copy().GET(
            'http://s.web2.qq.com/api/get_friend_uin2?tuin={0}&type=1&vfwebqq={1}&t={2}'.format(tuin, self.vfwebqq, _date_to_millis()),
            _REFERER_URL_2013)
        ret = json.loads(html)
        self.uin2acc[tuin] = ret['result']['account']
        return self.uin2acc[tuin]

    def get_user_friends(self):
        url = 'http://s.web2.qq.com/api/get_user_friends2'
        html = self.send_client.copy().POST(url, {'r': '{{"vfwebqq":"{0}","hash":"{1}"}}'.format(self.vfwebqq, self.hash_value)},
            _REFERER_URL_2013)
        ret = json.loads(html)
        if ret['retcode'] != 0:
            raise Exception('get_user_friends error')

    def get_group_name_list_mask(self):
        url = 'http://s.web2.qq.com/api/get_group_name_list_mask2'
        html = self.send_client.copy().POST(url, {'r': '{{"vfwebqq":"{0}","hash":"{1}"}}'.format(self.vfwebqq, self.hash_value)},
            _REFERER_URL_2013)
        ret = json.loads(html)
        if ret['retcode'] != 0:
            raise Exception('get_group_name_list_mask error')

    def get_discus_list(self):
        html = self.send_client.copy().GET( 'http://s.web2.qq.com/api/get_discus_list?clientid={0}&psessionid={1}&vfwebqq={2}&t={3}'.format(
            self.client_id,self.psessionid,self.vfwebqq,_date_to_millis()), _REFERER_URL_2013)
        ret = json.loads(html)
        if ret['retcode'] != 0:
            raise Exception('get_self_info error')

    def get_online_buddies(self):
        html = self.send_client.copy().GET( 'http://d1.web2.qq.com/channel/get_online_buddies2?vfwebqq={0}&clientid={1}&psessionid={2}&t={3}'.format(
            self.vfwebqq,self.client_id,self.psessionid,_date_to_millis()), _REFERER_URL)
        ret = json.loads(html)
        if ret['retcode'] != 0:
            raise Exception('get_online_buddies error')

    def get_discu_info(self, did):
        html = self.send_client.copy().GET( 'http://d1.web2.qq.com/channel/get_discu_info?did={0}&vfwebqq={1}&clientid={2}&psessionid={3}&t={4}'.format(
            did,self.vfwebqq,self.client_id,self.psessionid,_date_to_millis()), _REFERER_URL)
        ret = json.loads(html)
        if ret['retcode'] != 0:
            raise Exception('get_discu_info error')

    def get_recent_list(self):
        url = 'http://d1.web2.qq.com/channel/get_recent_list2'
        html = self.send_client.copy().POST(url, {'r': '{{"vfwebqq":"{0}","clientid":{1},"psessionid":"{2}"}}'.format(
            self.vfwebqq, self.client_id, self.psessionid)}, _REFERER_URL)
        ret = json.loads(html)
        if ret['retcode'] != 0:
            raise Exception('get_recent_list error')

    def get_single_long_nick(self, tuin):
        html = self.send_client.copy().GET( 'http://s.web2.qq.com/api/get_single_long_nick2?tuin={0}&vfwebqq={1}&t={2}'.format(
            tuin,self.vfwebqq,_date_to_millis()), _REFERER_URL_2013)
        ret = json.loads(html)
        if ret['retcode'] != 0:
            raise Exception('get_group_info_ext error')

    def get_group_info_ext(self, gcode):
        html = self.send_client.copy().GET( 'http://s.web2.qq.com/api/get_group_info_ext2?gcode={0}&vfwebqq={1}&t={2}'.format(
            gcode,self.vfwebqq,_date_to_millis()), _REFERER_URL_2013)
        ret = json.loads(html)
        if ret['retcode'] != 0:
            raise Exception('get_group_info_ext error')

    def get_friend_info(self, tuin):
        html = self.send_client.copy().GET( 'http://s.web2.qq.com/api/get_friend_info2?tuin={0}&vfwebqq={1}&clientid={2}&psessionid={3}&t={4}'.format(
            tuin,self.vfwebqq,self.client_id,self.psessionid,_date_to_millis()), _REFERER_URL_2013)
        ret = json.loads(html)
        if ret['retcode'] != 0:
            raise Exception('get_friend_info error')

    def change_status(self, status):
        # ['online','away','callme','busy','silent','hidden','offline']

        html = self.send_client.copy().GET( 'http://d1.web2.qq.com/channel/change_status2?newstatus={0}&clientid={1}&psessionid={2}&t={3}'.format(
            status,self.client_id,self.psessionid,_date_to_millis()), _REFERER_URL)
        ret = json.loads(html)
        if ret['retcode'] != 0:
            raise Exception('get_discu_info error')

