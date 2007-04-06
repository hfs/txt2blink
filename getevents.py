#!/usr/bin/env python

import datetime
import re
import sys
import time
import urllib
import xml.dom.minidom
from xml import xpath

def usage(name):
    print("Usage:   %s URL" % name)
    print("Example: %s %s" % (name, "http://www.kuze-potsdam.de/index.php/Kalender/Kalender"))

class Event:
    def __init__(self, date, content):
        self.date = date
        self.content = content

class EventFetcher:
    def __init__(self, url):
        self.url = url
    def getEvents(self):
        pass # abstract
    def toText(self, node):
        if node.nodeType == xml.dom.Node.TEXT_NODE:
            return node.nodeValue
        else:
            return "".join([self.toText(each) for each in node.childNodes])

class EventFetcherPmWiki(EventFetcher):
    def fetchEvents(self):
        events = []
        page = urllib.urlopen(self.url)
        charset = page.info().getparam('charset')
        pageContent = unicode(page.read(), charset).encode('utf-8')
        doc = xml.dom.minidom.parseString(pageContent)
        for event in xpath.Evaluate("//ul[@class='loglist']/li[(@class='wikilogpresent' or @class='wikilogfuture')]", doc):
            dateLink = event.firstChild.attributes['href'].value
            dateString = re.compile("/([0-9]+)$").search(dateLink).group(1)
            date = datetime.datetime(*(time.strptime(dateString, "%Y%m%d")[0:6]))
            events.append(Event(date, self.toText(event).strip()))
        return events

def main(argv=None):
    if argv == None:
        argv = sys.argv
    if len(argv) != 2:
        usage(argv[0])
        return 1
    for e in EventFetcherPmWiki(argv[1]).fetchEvents():
        print("[%s] %s" % (e.date.strftime("%Y%m%d"), e.content))

if __name__ == "__main__":
    main(sys.argv)

# vim: set ts=4 sw=4 et:
