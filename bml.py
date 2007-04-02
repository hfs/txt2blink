# txt2blink -- Ticker style Blinkenlight movies
# Copyright (C) 2007  Hermann Schwarting <hfs@gmx.de>
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the
# Free Software Foundation, Inc., 51 Franklin Street, Fifth Floor,
# Boston, MA  02110-1301, USA

import math
import numpy
from xml.dom import getDOMImplementation
from xml.dom.ext import PrettyPrint

class Bml:
    MIN_DELAY = 20
    DEFAULT_DELAY = 50

    def __init__(self, data):
        self.data = data
        self.n_frames, self.height, self.width = data.shape
        self.channels = 1
        self.maxval = numpy.max(data)
        self.bits = max(int(math.ceil(math.log(self.maxval + 1, 2))),1)
        self.duration = self.DEFAULT_DELAY * self.n_frames
        self.meta = {
                'title': '',
                'description': '',
                'creator': '',
                'author': '',
                'email': '',
                'url': '' }
        self.loop = False

    def addHeader(self, doc):
        header = doc.createElement('header')
        for each in ('title', 'description', 'creator', 'author', 'email', 'url'):
            if self.meta[each] != "":
                el = doc.createElement(each)
                el.appendChild(doc.createTextNode(self.meta[each]))
                header.appendChild(el)
        doc.documentElement.appendChild(header)

    def addFrames(self, doc):
        if self.bits <= 4:
            format = "%1x"
        else:
            format = "%2x"
        for f in range(self.n_frames):
            frame = doc.createElement('frame')
            frame.attributes['duration'] = str(self.DEFAULT_DELAY)
            for r in range(self.height):
                text = "".join([format % c for c in self.data[f,r,:]])
                row = doc.createElement('row')
                row.appendChild(doc.createTextNode(text))
                frame.appendChild(row)
            doc.documentElement.appendChild(frame)

    def write(self, writer):
        impl = getDOMImplementation()
        doctype = impl.createDocumentType("bml", None,
                "http://www.blinkenlights.de/dtd/bml.dtd")
        doc = impl.createDocument(None, "blm", doctype)
        root = doc.documentElement
        root.attributes['width'] = str(self.width)
        root.attributes['height'] = str(self.height)
        root.attributes['bits'] = str(self.bits)
        root.attributes['channels'] = str(self.channels)
        self.addHeader(doc)
        self.addFrames(doc)
        PrettyPrint(doc, writer, indent="\t", encoding="utf-8")

# vim: set ts=4 sw=4 et:
