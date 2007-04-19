#!/usr/bin/env python

"""Ticker style Blinkenlight movies

txt2blink.py [ -1 | -2 | -3 ] Text > out.bml

This program takes one line of text and creates an animation in the
Blinkenlights movie format. The text can be shown in 1, 2, or 3 lines with
matching font size.
"""

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

PROGRAM = "txt2blink"
VERSION = "0.1"

def version():
    print("%s version %s" % PROGRAM, VERSION)

class TextRenderer:
    """Renders a text string to a memory buffer"""
    _TYPE = numpy.uint8
    _FORMAT = cairo.FORMAT_A8

    def __init__(self, height, width, fontsize):
        """
        height: Height in pixels
        width: Intended width of a later blinkenlights movie.
               This width is used if an empty string is to be rendered.
        fontsize: Font size in pixels. A suitable font is chosen for you
        """
        self.height = height
        self.width = width
        self.fontsize = fontsize

    def render(self, text):
        """Render a text string.

        text: Render this text
        Returns a 2-dimensional array indexed [height,width]. The width is
        dynamic and chosen such that the text fits exactly. The values
        represent grayscales.
        """
        if len(text) < 1:
            return numpy.zeros([self.height, self.width], self._TYPE)
        width = len(text) * self.height * 2
        data = numpy.zeros([self.height, width], self._TYPE)
        surface = cairo.ImageSurface.create_for_data(data, self._FORMAT, width, self.height)
        c = cairo.Context(surface)
        c.set_source_rgba(1, 1, 1, 0)
        c.paint()
        c.set_source_rgba(0, 0, 0, 1)
        c.select_font_face(self._chooseFont(), cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
        # The slight horizontal scaling compensates for the non-square pixels.
        # The font matrix can set the size but *else* is ineffective with bitmap fonts.
        c.set_font_matrix(cairo.Matrix(self.fontsize*1.2, 0, 0, self.fontsize, 0, 0))
        c.set_font_options(cairo.FontOptions(cairo.HINT_METRICS_ON, cairo.HINT_STYLE_FULL))
        fascent, fdescent, fheight, fxadvance, fyadvance = c.font_extents()
        xbearing, ybearing, awidth, aheight, xadvance, yadvance = c.text_extents(text)
        c.move_to(xbearing, self.height-fdescent)
        c.show_text(text)
        surface.flush()
        return data[:,0:int(xadvance+xbearing)]

    def _chooseFont(self):
        """Choose a suitable font for the font size."""
        if self.fontsize <= 8:
            return 'Fixed'
        # "DejaVu Sans" is not a good choice, as 'f' may be mistaken as 't' and
        # 'i' is displayed without dot.
        return 'Arial'

class Scroller:
    """Make a side scrolling animation from an image."""
    _TYPE = numpy.uint8
    _MINHEIGHT = 6

    def __init__(self, height, width):
        """
        height: Height of the resulting animation
        width: Width of the resulting animation
        """
        self.height = height
        self.width = width

    def scroll(self, data, lines=1):
        """Make an animation from an image with a certain number of lines.

        data: Input image. The height should not be larger than the target
              animation.
        lines: If > 1, divide the output into this number of stripes and shift
               the input image though them from bottom to top.

        Returns a 3-dimensional array indexed [frame, height, width].
        """
        if lines < 1:
            lines = 1
        if lines > self.height / self._MINHEIGHT:
            lines = self.height / self._MINHEIGHT
        hdata, wdata = data.shape
        hline = min(self.height/lines, hdata)
        frames = numpy.zeros(
                [wdata + self.width * lines, self.height, self.width],
                self._TYPE)
        for w in range(wdata):
            for x in range(self.width):
                for l in range(lines):
                    y = int(math.ceil(float(self.height)/lines*l))
                    frames[w + x + (lines-l-1) * self.width,
                            y:y+hline, self.width - x - 1 ] = data[0:hline, w]
        return frames

class Txt2Blink:
    """Side scrolling blinkenlights animation from text."""
    HEIGHT = 20;
    WIDTH = 26;
    def __init__(self, height=HEIGHT, width=WIDTH, lines=1):
        """Dimensions of the target animation"""
        self.lines = lines
        self.renderer = TextRenderer(height/lines, width, height/lines)
        self.scroller = Scroller(height, width)
    def txt2bml(self, text):
        """Render text to a blinkenlights movie.

        Returns an instance of bml.Bml
        """
        data = self.renderer.render(text)
        data = self.scroller.scroll(data, self.lines)
        data /= 32
        b = bml.Bml(data)
        b.meta['creator'] = PROGRAM + "/" + VERSION
        b.meta['description'] = text
        return b

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
            print(__doc__)
            return 0
        if o in ("-1", "--1", "-2", "--2", "-3", "--3"):
            modus = int(o[-1])
    if len(args) < 1:
        print(__doc__)
        return(2)
    text = " ".join(args)
    Txt2Blink(lines=modus).txt2bml(text).write(sys.stdout)
    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv))

# vim: set ts=4 sw=4 et:
