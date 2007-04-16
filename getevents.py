#!/usr/bin/env python

"""Extract future events from a PmWiki calendar

getevents.py URL

Example: getevents.py http://www.kuze-potsdam.de/index.php/Kalender/Kalender

The information is printed in pairs of two lines: The first contains the date
in the format "yyyymmdd", the second the event summarization.
"""

import datetime
import re
import sys
import time
import urllib
import xml.dom.minidom
from xml import xpath

class Event:
    """Event representation
    .date: instance of datetime
    .content: string
    """
    def __init__(self, date, content):
        self.date = date
        self.content = content

class EventFetcher:
    def __init__(self, url):
        self.url = url
    def getEvents(self):
        """abstract method"""
        pass # abstract
    def toText(self, node):
        """Extract the text in an XML subtree"""
        if node.nodeType == xml.dom.Node.TEXT_NODE:
            return node.nodeValue
        else:
            return "".join([self.toText(each) for each in node.childNodes])

class EventFetcherPmWiki(EventFetcher):
    def getEvents(self):
        """Return a list of Events"""
        events = []
        page = urllib.urlopen(self.url)
        charset = page.info().getparam('charset')
        pageContent = unicode(page.read(), charset).encode('utf-8')
        doc = xml.dom.minidom.parseString(pageContent)
        # This XPath query is the essential line
        for event in xpath.Evaluate("descendant::ul[@class='loglist']/li[(@class='wikilogpresent' or @class='wikilogfuture')]", doc):
            dateLink = event.firstChild.attributes['href'].value
            dateString = re.compile("/([0-9]+)$").search(dateLink).group(1)
            date = datetime.datetime(*(time.strptime(dateString, "%Y%m%d")[0:6]))
            events.append(Event(date, unicode(self.toText(event).strip())))
        return events

def main(argv=None):
    if argv == None:
        argv = sys.argv
    if len(argv) != 2:
        print(__doc__)
        return 1
    for e in EventFetcherPmWiki(argv[1]).getEvents():
        print(e.date.strftime("%Y%m%d"))
        print(e.content.encode('utf-8'))

if __name__ == "__main__":
    main(sys.argv)

# vim: set ts=4 sw=4 et:
