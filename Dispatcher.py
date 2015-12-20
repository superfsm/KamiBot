# -*- coding: utf-8 -*-

# Copyright (C) <2015>  Shaoming Feng

# This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
# This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
# You should have received a copy of the GNU General Public License along with this program.  If not, see <http://www.gnu.org/licenses/>.

import sys, importlib, logging, traceback
import Config

class Dispatcher:

    #QQ = None
    #msgQ = None
    #pipeline = []

    def __init__(self, QQ):
        self.QQ = QQ
        self.msgQ = QQ.msgQ
        self.pipeline = []

        self._reload_pipeline()

    def _reload_pipeline(self):


        # Tell modules to unload
        for cls in self.pipeline:
            cls.unload()

        # Cleanup
        self.pipeline = []

        # Reload module
        reload(Config)
        for m in Config.addons:
            try:
                m = 'addons.' + m
                if m in sys.modules:
                    module = reload(sys.modules[m])
                else:
                    module = importlib.import_module(m)
                cls = getattr(module, 'Handler')
                self.pipeline.append(cls(self.QQ))
            except:
                traceback.print_exc()
                logging.error("Addon loading failed")

    def start(self):
        while True:
            logging.debug('Handling next message')
            msg = self.msgQ.get()
            if self._root_process(msg):
                continue

            reply_txt = ''
            for h in self.pipeline:
                try:
                    ret = h.process(msg)
                    if isinstance(ret, tuple):
                        if not reply_txt:
                            reply_txt += ret[1]
                        else:
                            reply_txt += "\n" + ret[1]
                        if ret[0]:
                            break
                    elif ret:   # isinstance(ret, boolean):
                            break
                except:
                    traceback.print_exc
                    logging.exception("An addon failed")
            try:
                if reply_txt:
                    msg.send_txt(reply_txt)
            except:
                logging.exception("Message send failed")

    # superuser command
    def _root_process(self, msg):

        sender = self.QQ.get_friend_uin(msg.from_sender)
        if not sender in Config.group_root:
            return False

        txt = msg.from_txt

        reply = ''
        if txt in ('##!ping', '##！ping'):
            reply = 'Pong!'
        elif txt in ('##!list', '##！list'):
            reply += "Loaded module:\n"
            for m in Config.addons:
                reply += m + '\n'
            reply.strip()
        elif txt in ('##!reload', '##！reload'):
            self._reload_pipeline()
            reply = 'Modules reloaded!'
        else:
            return False
        reply = '[{0}] {1}'.format(Config.name_root, reply)
        msg.send_txt(reply)
        return True


















