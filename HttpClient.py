# -*- coding: utf-8 -*-

# Copyright (C) <2015>  Shaoming Feng

# This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
# This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
# You should have received a copy of the GNU General Public License along with this program.  If not, see <http://www.gnu.org/licenses/>.

import requests
import logging

class HttpClient:
    debug = True
    session = requests.Session()
    r = None
    
    def __init__(self):
        self.session.headers.update({
            'Accept': 'application/javascript, */*;q=0.8',
            'User-Agent': 'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; WOW64; Trident/5.0)',
        })

    def GET(self, url, refer=None):
        try:
            if refer is not None:
                self.session.headers.update({'Referer': refer})
            self.r = self.session.get(url, timeout = 120)
            logging.debug("STATUS CODE = %d",self.r.status_code)
            if self.debug:
                logging.debug(self.r.text)
            return self.r.text
        except:
            logging.exception('GET Exception')

    def POST(self, url, data, refer=None):
        try:
            if refer is not None:
                self.session.headers.update({'Referer': refer})
            self.r = self.session.post(url, data = data, timeout = 120)
            logging.debug("STATUS CODE = %d",self.r.status_code)
            if self.debug:
                logging.debug(self.r.text)
            return self.r.text
        except:
            logging.exception('GET Exception')

    def download(self, url, path):
        try:
            output = open(path, 'wb')
            output.write(self.session.get(url).content)
            output.close()
        except:
            logging.exception('Download error')

    def getCookie(self, key):
        print self.r.cookies
        try:
            return self.r.cookies[key]
        except:
            return ''
