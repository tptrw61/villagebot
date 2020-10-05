
from datetime import datetime, timedelta
import xml.etree.ElementTree as ET
import json
import requests
from collections import namedtuple
import pytz

def getHeaderDate(dt):
    return dt.strftime('%a, %d %b %Y %H:%M:%S GMT')

def makeUTC(d):
    if not type(d) is datetime:
        raise TypeError("d must be a datetime object")
    if d.tzinfo == None:
        return pytz.UTC.localize(d)
    return d


ResponseTuple = namedtuple('ResponseTuple', ['data', 'code', 'reason'])

#include '/feed' in the url
def getModifiedSinceRSS(url, date_):
    if not type(url) is str:
        raise TypeError("url must be a string")
    if not type(date_) is datetime:
        raise TypeError("date must be a datetime object")
    date = makeUTC(date_)

    r = requests.get(url, headers={'If-Modified-Since': getHeaderDate(date)})

    #for now ignore errors
    if not r.ok:
        pass

    if r.status_code == 304:
        return ResponseTuple([], 304, r.reason)

    if r.status_code == 200: #response is OK
        root = ET.fromstring(r.text)
        channel = root.find('channel')
        links = []
        #i = 1
        for item in channel.findall('item'):
            #print(f'iter: {i}')
            pubDateNode = item.find('pubDate')
            if pubDateNode is None:
                #print('None')
                pass
            else:
                #print('found')
                pubDate = makeUTC(datetime.strptime(pubDateNode.text,
                                       '%a, %d %b %Y %H:%M:%S %z'))
                #print(pubDate)
                if date < pubDate: #if date preceeds pubDate
                    links.append(item.find('link').text)
            #i += 1
        return ResponseTuple(links, 200, r.reason)

    return ResponseTuple([], r.status_code, r.reason)

def getModifiedSinceJSON(url, date):
    if not type(url) is str:
        raise TypeError("url must be a string")
    if not type(date) is datetime:
        raise TypeError("date must be a datetime object")

    r = requests.get(url, headers={'If-Modified-Since': getHeaderDate(date)})
    
    #for now ignore errors
    if not r.ok:
        pass

    if r.status_code == 304:
        return ResponseTuple(None, 304, r.reason)

    if r.status_code == 200:
        return ResponseTuple(json.loads(r.text), 200, r.reason)

    return ResponseTuple(None, r.status_code, r.reason)
