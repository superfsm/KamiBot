# -*- coding: utf-8 -*-

# Copyright (C) <2015>  Shaoming Feng

# This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
# This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
# You should have received a copy of the GNU General Public License along with this program.  If not, see <http://www.gnu.org/licenses/>.

class AbstractHandler:

    #QQ = None

    def __init__(self, QQ):
        self.QQ = QQ
        self.init()

    def init(self):
        pass

    def name(self):
        return "[name]"

    #return true if you consume the message
    def process(self, msg):
        return True, ''
        #or you can a single boolean

    def unload(self):
        pass

