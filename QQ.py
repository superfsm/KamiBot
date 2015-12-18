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
from PIL import Image

from HttpClient import HttpClient

_SMART_QQ_URL = 'http://w.qq.com/login.html'
_QR_PATH = './QR.jpg'
_REFERER_URL = 'http://d1.web2.qq.com/proxy.html?v=20151105001&callback=1&id=2'

def _display_QRCode():
    img = Image.open(_QR_PATH)
    img.show()

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
        self.http_client = HttpClient()
        
        self.username = ''
        
        self.client_id = 53999199
        self.ptwebqq = ''
        self.psessionid = ''
        self.vfwebqq = ''
        self.account = 0

    def QR_login(self):
        logging.info('Connecting to QQ server...')
        
        # For naming convinience
        http_client = self.http_client
        
        
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
            logging.info("Please scan the downloaded QR code")
            thread.start_new_thread(_display_QRCode,())

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
            
        logging.info("QR code scaned, now logging in...")

        # Get user nickname
        self.username = ret[11]
        
        # Browse proxy urls to get correct cookies
        http_client.GET(ret[5])
        http_client.GET('http://web2.qq.com/web2_cookie_proxy.html')
        self.ptwebqq = http_client.getCookie('ptwebqq')

        # Login
        retry = 0
        ret = {}
        while True:
            retry += 1
            try:
                html = http_client.POST('http://d1.web2.qq.com/channel/login2', 
                    {'r': '{{"ptwebqq":"{0}","clientid":{1},"psessionid":"{2}","status":"online"}}'.format(self.ptwebqq, self.client_id, self.psessionid)},
                    _REFERER_URL)
                ret = json.loads(html)
                break
            except:
                if retry < 3:
                    logging.exception("login failed, retrying...")
                else:
                    logging.exception("login failed")
                    return False

        logging.debug(_dump_json(ret))
        if ret['retcode'] != 0:
            logging.error("login return code: %s", str(ret['retcode']))
            return False

        self.vfwebqq = ret['result']['vfwebqq']
        self.psessionid = ret['result']['psessionid']
        self.account = ret['result']['uin']

        logging.info("QQ: {0} login successfully, Username：{1}".format(self.account, self.username))
        print "Welcome, " + self.username.decode('utf-8').encode('gb2312') + "!"
        return True
        
    def poll_loop(self):
        while True:
            self.poll()

    def poll(self, error_times=0):
        
        if error_times >= 5:
            if not self.relogin():
                raise IOError("Account offline.")
            else:
                error_times = 0

        # poll
        html = self.http_client.POST('http://d1.web2.qq.com/channel/poll2', {
            'r': '{{"ptwebqq":"{1}","clientid":{2},"psessionid":"{0}","key":""}}'.format(self.psessionid, 
                                                                                         self.ptwebqq,
                                                                                         self.client_id)
        }, _REFERER_URL)
        if html == "":
            return
        
        ret = json.loads(html)
        logging.debug(_dump_json(ret))
        return
        
        ret_code = ret['retcode']

        if ret_code in (102,):
            logging.info("received retcode: " + str(ret_code) + ": No message.")
            return

        if ret_code in (103,):
            logging.warning("received retcode: " + str(ret_code) + ": Check error. retrying.." + str(error_times))
            time.sleep(1)
            return self.check_msg(error_times + 1)

        if ret_code in (121,):
            logging.warning("received retcode: " + str(ret_code))
            return self.check_msg(5)

        elif ret_code == 0:
            msg_list = []
            pm_list = []
            sess_list = []
            group_list = []
            notify_list = []
            for msg in ret['result']:
                ret_type = msg['poll_type']
                if ret_type == 'message':
                    pm_list.append(PmMsg(msg))
                elif ret_type == 'group_message':
                    group_list.append(GroupMsg(msg))
                elif ret_type == 'sess_message':
                    sess_list.append(SessMsg(msg))
                elif ret_type == 'input_notify':
                    notify_list.append(InputNotify(msg))
                elif ret_code == 'kick_message':
                    notify_list.append(KickMessage(msg))
                else:
                    logging.warning("unknown message type: " + str(ret_type) + "details:    " + str(msg))

            group_list.sort(key=lambda x: x.msg_id)
            msg_list += pm_list + sess_list + group_list + notify_list
            if not msg_list:
                return
            return msg_list

        elif ret_code == 100006:
            logging.warning("POST data error")
            return

        elif ret_code == 116:
            self.ptwebqq = ret['p']
            logging.info("ptwebqq updated.")
            return

        else:
            logging.warning("unknown retcode " + str(ret_code))
            return
    
    def __getGroupSig(self, guin, tuin, service_type=0):
        key = '%s --> %s' % (guin, tuin)
        if key not in self.__groupSig_list:
            url = "http://d1.web2.qq.com/channel/get_c2cmsg_sig2?id=%s&to_uin=%s&service_type=%s&clientid=%s&psessionid=%s&t=%d" % (
                guin, tuin, service_type, self.client_id, self.psessionid, int(time.time() * 100))
            response = self.http_client.GET(url)
            rsp_json = json.loads(response)
            if rsp_json["retcode"] != 0:
                return ""
            sig = rsp_json["result"]["value"]
            self.__groupSig_list[key] = sig
        if key in self.__groupSig_list:
            return self.__groupSig_list[key]
        return ""

    def relogin(self, error_times=0):
        if error_times >= 10:
            return False
        try:
            html = self.http_client.POST('http://d1.web2.qq.com/channel/login2', {
                'r': '{{"ptwebqq":"{0}","clientid":{1},"psessionid":"{2}","key":"","status":"online"}}'.format(
                    self.ptwebqq,
                    self.client_id,
                    self.psessionid)
            }, self.default_config.conf.get("global", "connect_referer"))
            logging.debug("relogin html:  " + str(html))
            ret = json.loads(html)
            self.vfwebqq = ret['result']['vfwebqq']
            self.psessionid = ret['result']['psessionid']
            return True
        except:
            logging.info("login fail, retryng..." + str(error_times))
            return self.relogin(error_times + 1)

    # 查询QQ号，通常首次用时0.2s，以后基本不耗时
    def uin_to_account(self, tuin):
        """
        将uin转换成用户昵称
        :param tuin:
        :return:str 用户昵称
        """
        uin_str = str(tuin)
        if uin_str not in self.friend_list:
            try:
                logging.info("Requesting the account by uin:    " + str(tuin))
                info = json.loads(self.http_client.GET(
                    'http://s.web2.qq.com/api/get_friend_uin2?tuin={0}&type=1&vfwebqq={1}'.format(uin_str,
                                                                                                  self.vfwebqq),
                    self.default_config.conf.get("global", "connect_referer")))
                logging.debug("uin_request html:    " + str(info))
                if info['retcode'] != 0:
                    raise TypeError('uin to account result error')
                info = info['result']
                self.friend_list[uin_str] = info['account']

            except:
                logging.exception("uin_to_account")

        assert isinstance(uin_str, str), "tuin is not string"
        try:
            return self.friend_list[uin_str]
        except:
            logging.exception("uin_to_account")
            logging.debug("now uin list:    " + str(self.friend_list))

    # 获取自己的信息
    def get_self_info2(self):
        """
        获取自己的信息
        get_self_info2
        {"retcode":0,"result":{"birthday":{"month":1,"year":1989,"day":30},"face":555,"phone":"","occupation":"","allow":1,"college":"","uin":2609717081,"blood":0,"constel":1,"lnick":"","vfwebqq":"68b5ff5e862ac589de4fc69ee58f3a5a9709180367cba3122a7d5194cfd43781ada3ac814868b474","homepage":"","vip_info":0,"city":"青岛","country":"中国","personal":"","shengxiao":5,"nick":"要有光","email":"","province":"山东","account":2609717081,"gender":"male","mobile":""}}
        :return:dict
        """
        if not self.__self_info:
            url = "http://s.web2.qq.com/api/get_self_info2"
            response = self.http_client.GET(url)
            rsp_json = json.loads(response)
            if rsp_json["retcode"] != 0:
                return {}
            self.__self_info = rsp_json["result"]
        return self.__self_info

    # 获取好友详情信息
    def get_friend_info2(self, tuin):
        """
        获取好友详情信息
        get_friend_info2
        {"retcode":0,"result":{"face":0,"birthday":{"month":1,"year":1989,"day":30},"occupation":"","phone":"","allow":1,"college":"","uin":3964575484,"constel":1,"blood":3,"homepage":"http://blog.lovewinne.com","stat":20,"vip_info":0,"country":"中国","city":"","personal":"","nick":" 信","shengxiao":5,"email":"John123951@126.com","province":"山东","gender":"male","mobile":"158********"}}
        :return:dict
        """
        url = "http://s.web2.qq.com/api/get_friend_info2?tuin=%s&vfwebqq=%s&clientid=%s&psessionid=%s&t=%s" % (
            tuin, self.vfwebqq, self.client_id, self.psessionid, int(time.time() * 100))
        response = self.http_client.GET(url)
        rsp_json = json.loads(response)
        if rsp_json["retcode"] != 0:
            return {}
        return rsp_json["result"]

    # 获取好友的签名信息
    def get_single_long_nick2(self, tuin):
        """
        获取好友的签名信息
        get_single_long_nick2
        {"retcode":0,"result":[{"uin":3964575484,"lnick":"幸福，知道自己在哪里，知道下一个目标在哪里，心不累~"}]}
        :return:dict
        """
        url = "http://s.web2.qq.com/api/get_single_long_nick2?tuin=%s&vfwebqq=%s&t=%s" % (
            tuin, self.vfwebqq, int(time.time() * 100))
        response = self.http_client.GET(url)
        rsp_json = json.loads(response)
        if rsp_json["retcode"] != 0:
            return {}
        return rsp_json["result"]

    # 获取群信息（对于易变的信息，请在外层做缓存处理）
    def get_group_info_ext2(self, gcode):
        """
        获取群信息
        get_group_info_ext2
        {"retcode":0,"result":{"stats":[],"minfo":[{"nick":" 信","province":"山东","gender":"male","uin":3964575484,"country":"中国","city":""},{"nick":"崔震","province":"","gender":"unknown","uin":2081397472,"country":"","city":""},{"nick":"云端的猫","province":"山东","gender":"male","uin":3123065696,"country":"中国","city":"青岛"},{"nick":"要有光","province":"山东","gender":"male","uin":2609717081,"country":"中国","city":"青岛"},{"nick":"小莎机器人","province":"广东","gender":"female","uin":495456232,"country":"中国","city":"深圳"}],"ginfo":{"face":0,"memo":"http://hujj009.ys168.com\r\n0086+区(没0)+电话\r\n0086+手机\r\nhttp://john123951.xinwen365.net/qq/index.htm","class":395,"fingermemo":"","code":3943922314,"createtime":1079268574,"flag":16778241,"level":0,"name":"ぁQQぁ","gid":3931577475,"owner":3964575484,"members":[{"muin":3964575484,"mflag":192},{"muin":2081397472,"mflag":65},{"muin":3123065696,"mflag":128},{"muin":2609717081,"mflag":0},{"muin":495456232,"mflag":0}],"option":2},"cards":[{"muin":3964575484,"card":"●s.Εx2(22222)□"},{"muin":495456232,"card":"小莎机器人"}],"vipinfo":[{"vip_level":0,"u":3964575484,"is_vip":0},{"vip_level":0,"u":2081397472,"is_vip":0},{"vip_level":0,"u":3123065696,"is_vip":0},{"vip_level":0,"u":2609717081,"is_vip":0},{"vip_level":0,"u":495456232,"is_vip":0}]}}
        :return:dict
        """
        if gcode == 0:
            return {}
        try:
            url = "http://s.web2.qq.com/api/get_group_info_ext2?gcode=%s&vfwebqq=%s&t=%s" % (
                gcode, self.vfwebqq, int(time.time() * 100))
            response = self.http_client.GET(url)
            rsp_json = json.loads(response)
            if rsp_json["retcode"] != 0:
                return {}
            return rsp_json["result"]
        except Exception as ex:
            logging.warning("get_group_info_ext2. Error: " + str(ex))
            return {}

    # 发送群消息
    def send_qun_msg(self, guin, reply_content, msg_id, fail_times=0):
        fix_content = str(reply_content.replace("\\", "\\\\\\\\").replace("\n", "\\\\n").replace("\t", "\\\\t")).decode(
            "utf-8")
        rsp = ""
        try:
            req_url = "http://d1.web2.qq.com/channel/send_qun_msg2"
            data = (
                ('r',
                 '{{"group_uin":{0}, "face":564,"content":"[\\"{4}\\",[\\"font\\",{{\\"name\\":\\"Arial\\",\\"size\\":\\"10\\",\\"style\\":[0,0,0],\\"color\\":\\"000000\\"}}]]","clientid":"{1}","msg_id":{2},"psessionid":"{3}"}}'.format(
                     guin, self.client_id, msg_id, self.psessionid, fix_content)),
                ('clientid', self.client_id),
                ('psessionid', self.psessionid)
            )
            rsp = self.http_client.POST(req_url, data, self.default_config.conf.get("global", "connect_referer"))
            rsp_json = json.loads(rsp)
            if rsp_json['retcode'] != 0:
                raise ValueError("reply group chat error" + str(rsp_json['retcode']))
            logging.info("send_qun_msg: Reply successfully.")
            logging.debug("send_qun_msg: Reply response: " + str(rsp))
            return rsp_json
        except:
            logging.exception("send_qun_msg exception")
            if fail_times < 5:
                logging.warning("send_qun_msg: Response Error.Wait for 2s and Retrying." + str(fail_times))
                logging.debug(rsp)
                time.sleep(2)
                self.send_qun_msg(guin, reply_content, msg_id, fail_times + 1)
            else:
                logging.warning("send_qun_msg: Response Error over 5 times.Exit.reply content:" + str(reply_content))
                return False

    # 发送私密消息
    def send_buddy_msg(self, tuin, reply_content, msg_id, fail_times=0):
        fix_content = str(reply_content.replace("\\", "\\\\\\\\").replace("\n", "\\\\n").replace("\t", "\\\\t")).decode(
            "utf-8")
        rsp = ""
        try:
            req_url = "http://d1.web2.qq.com/channel/send_buddy_msg2"
            data = (
                ('r',
                 '{{"to":{0}, "face":594, "content":"[\\"{4}\\", [\\"font\\", {{\\"name\\":\\"Arial\\", \\"size\\":\\"10\\", \\"style\\":[0, 0, 0], \\"color\\":\\"000000\\"}}]]", "clientid":"{1}", "msg_id":{2}, "psessionid":"{3}"}}'.format(
                     tuin, self.client_id, msg_id, self.psessionid, fix_content)),
                ('clientid', self.client_id),
                ('psessionid', self.psessionid)
            )
            rsp = self.http_client.POST(req_url, data, self.default_config.conf.get("global", "connect_referer"))
            rsp_json = json.loads(rsp)
            if rsp_json['retcode'] != 0:
                raise ValueError("reply pmchat error" + str(rsp_json['retcode']))
            logging.info("Reply successfully.")
            logging.debug("Reply response: " + str(rsp))
            return rsp_json
        except:
            if fail_times < 5:
                logging.warning("Response Error.Wait for 2s and Retrying." + str(fail_times))
                logging.debug(rsp)
                time.sleep(2)
                self.send_buddy_msg(tuin, reply_content, msg_id, fail_times + 1)
            else:
                logging.warning("Response Error over 5 times.Exit.reply content:" + str(reply_content))
                return False

    # 发送临时消息
    def send_sess_msg2(self, tuin, reply_content, msg_id, group_sig, service_type=0, fail_times=0):
        fix_content = str(reply_content.replace("\\", "\\\\\\\\").replace("\n", "\\\\n").replace("\t", "\\\\t")).decode(
            "utf-8")
        rsp = ""
        try:
            req_url = "http://d1.web2.qq.com/channel/send_sess_msg2"
            data = (
                ('r',
                 '{{"to":{0}, "face":594, "content":"[\\"{4}\\", [\\"font\\", {{\\"name\\":\\"Arial\\", \\"size\\":\\"10\\", \\"style\\":[0, 0, 0], \\"color\\":\\"000000\\"}}]]", "clientid":"{1}", "msg_id":{2}, "psessionid":"{3}", "group_sig":"{5}", "service_type":{6}}}'.format(
                     tuin,
                     self.client_id,
                     msg_id,
                     self.psessionid,
                     fix_content,
                     group_sig,
                     service_type)
                 ),
                ('clientid', self.client_id),
                ('psessionid', self.psessionid),
                ('group_sig', group_sig),
                ('service_type', service_type)
            )
            rsp = self.http_client.POST(req_url, data, self.default_config.conf.get("global", "connect_referer"))
            rsp_json = json.loads(rsp)
            if rsp_json['retcode'] != 0:
                raise ValueError("reply sess chat error" + str(rsp_json['retcode']))
            logging.info("Reply successfully.")
            logging.debug("Reply response: " + str(rsp))
            return rsp_json
        except:
            if fail_times < 5:
                logging.warning("Response Error.Wait for 2s and Retrying." + str(fail_times))
                logging.debug(rsp)
                time.sleep(2)
                self.send_sess_msg2(tuin, reply_content, msg_id, group_sig, service_type, fail_times + 1)
            else:
                logging.warning("Response Error over 5 times.Exit.reply content:" + str(reply_content))
                return False

    # 主动发送临时消息
    def send_sess_msg2_fromGroup(self, guin, tuin, reply_content, msg_id, service_type=0, fail_times=0):
        group_sig = self.__getGroupSig(guin, tuin, service_type)
        fix_content = str(reply_content.replace("\\", "\\\\\\\\").replace("\n", "\\\\n").replace("\t", "\\\\t")).decode(
            "utf-8")
        rsp = ""
        try:
            req_url = "http://d1.web2.qq.com/channel/send_sess_msg2"
            data = (
                ('r',
                 '{{"to":{0}, "face":594, "content":"[\\"{4}\\", [\\"font\\", {{\\"name\\":\\"Arial\\", \\"size\\":\\"10\\", \\"style\\":[0, 0, 0], \\"color\\":\\"000000\\"}}]]", "clientid":"{1}", "msg_id":{2}, "psessionid":"{3}", "group_sig":"{5}", "service_type":{6}}}'.format(
                     tuin,
                     self.client_id,
                     msg_id,
                     self.psessionid,
                     fix_content,
                     group_sig,
                     service_type)
                 ),
                ('clientid', self.client_id),
                ('psessionid', self.psessionid),
                ('group_sig', group_sig),
                ('service_type', service_type)
            )
            rsp = self.http_client.POST(req_url, data, self.default_config.conf.get("global", "connect_referer"))
            rsp_json = json.loads(rsp)
            if rsp_json['retcode'] != 0:
                raise ValueError("reply sess chat error" + str(rsp_json['retcode']))
            logging.info("send_sess_msg2_fromGroup: Reply successfully.")
            logging.debug("send_sess_msg2_fromGroup: Reply response: " + str(rsp))
            return rsp_json
        except:
            if fail_times < 5:
                logging.warning("send_sess_msg2_fromGroup: Response Error.Wait for 2s and Retrying." + str(fail_times))
                logging.debug(rsp)
                time.sleep(2)
                self.send_sess_msg2_fromGroup(guin, tuin, reply_content, msg_id, service_type, fail_times + 1)
            else:
                logging.warning("send_sess_msg2_fromGroup: Response Error over 5 times.Exit.reply content:" + str(reply_content))
                return False
