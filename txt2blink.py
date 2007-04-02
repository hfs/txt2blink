#!/usr/bin/env python
#
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

import bml
import cairo
import getopt
import math
import numpy
import sys

PROGRAM = "txt2blinken"
VERSION = "0.1"
HEIGHT = 20;
WIDTH = 26;

def usage():
    print("Usage: %s [ -1 | -2 | -3 ] Text > out.bml" % sys.argv[0])

def version():
    print("%s version %s" % PROGRAM, VERSION)

class TextRenderer:
    TYPE = numpy.uint8
    FORMAT = cairo.FORMAT_A8

    def __init__(self, height, width, fontsize):
        self.height = height
        self.width = width
        self.fontsize = fontsize

    def render(self, text):
        if len(text) < 1:
            return numpy.zeros([self.height, self.width], self.TYPE)
        width = len(text) * self.height * 2
        data = numpy.zeros([self.height, width], self.TYPE)
        surface = cairo.ImageSurface.create_for_data(data, self.FORMAT, width, self.height)
        c = cairo.Context(surface)
        c.set_source_rgba(1, 1, 1, 0)
        c.paint()
        c.set_source_rgba(0, 0, 0, 1)
        c.select_font_face(self.chooseFont(), cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
        # The font matrix can set the size but else is *ineffective* with bitmap fonts
        c.set_font_matrix(cairo.Matrix(self.fontsize*1.2, 0, 0, self.fontsize, 0, 0))
        c.set_font_options(cairo.FontOptions(cairo.HINT_METRICS_ON, cairo.HINT_STYLE_FULL))
        fascent, fdescent, fheight, fxadvance, fyadvance = c.font_extents()
        xbearing, ybearing, awidth, aheight, xadvance, yadvance = c.text_extents(text)
        c.move_to(xbearing, self.height-fdescent)
        c.show_text(text)
        surface.flush()
        return data[:,0:int(xadvance+xbearing)]

    def chooseFont(self):
        if self.fontsize <= 8:
            return 'Fixed'
        return 'DejaVu Sans'

class Scroller:
    TYPE = numpy.uint8
    MINHEIGHT = 6

    def __init__(self, height, width):
        self.height = height
        self.width = width

    def scroll(self, data, lines=1):
        if lines < 1:
            lines = 1
        if lines > self.height / self.MINHEIGHT:
            lines = self.height / self.MINHEIGHT
        hdata, wdata = data.shape
        hline = min(self.height/lines, hdata)
        frames = numpy.zeros(
                [wdata + self.width * lines, self.height, self.width],
                self.TYPE)
        for w in range(wdata):
            for x in range(self.width):
                for l in range(lines):
                    y = int(math.ceil(float(self.height)/lines*l))
#                    print(w + x + (lines-l-1) * self.width, l*hline,(l+1)*hline-1, self.width - x - 1)
                    frames[w + x + (lines-l-1) * self.width,
                            y:y+hline, self.width - x - 1 ] = data[0:hline, w]
        return frames

def main(argv=None):
    modus = 1
    if argv is None:
        argv = sys.argv
    try:
        opts, args = getopt.getopt(argv[1:], "123h", ["1", "2", "3", "help"])
    except getopt.error, msg:
        print(msg)
        print("For help use --help")
        return(2)
    for o, a in opts:
        if o in ("-h", "--help"):
            usage()
            return 0
        if o in ("-1", "--1", "-2", "--2", "-3", "--3"):
            modus = int(o[-1])
    if len(args) < 1:
        usage()
        return(2)
    text = " ".join(args)
    data = TextRenderer(HEIGHT/modus, WIDTH, HEIGHT/modus).render(text)
    data = Scroller(HEIGHT, WIDTH).scroll(data, modus)
    data /= 32;
    b = bml.Bml(data)
    b.meta['creator'] = PROGRAM + "/" + VERSION
    b.meta['description'] = text
    b.write(sys.stdout)
    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv))

# vim: set ts=4 sw=4 et:
