import json
import re
from datetime import timedelta, datetime
from itertools import islice
from time import clock, sleep

from lxml import  html
from lxml.etree import HTMLParser, fromstring
from httplib2 import Http
from pytz import timezone

from source.channels.nashalvch import channel_code
from schedule import Schedule
from util import extract_text

source_tz = timezone('Europe/Riga')

today = datetime.now(source_tz).date()
monday = today - timedelta(today.weekday())
del today

http = Http()
parser = HTMLParser()

# Avoid 'robot' detection
THROTTLE = 2
BURST = 10

counter = BURST
last_clock = -THROTTLE


def fetch(path):
    global counter, last_clock

    counter -= 1
    next_clock = clock()

    if counter > 0:
        tosleep = 0
    else:
        counter = BURST
        tosleep = THROTTLE - (next_clock - last_clock)

    if tosleep > 0:
        sleep(tosleep)
        last_clock += THROTTLE
    else:
        last_clock = next_clock

    url = 'http://www.nasha.lv/rus/razvlechenija/tv/'
    return http.request(url + path)[1]


def get_summary(sum_id):
    query = '?json=1&action=get_announce&announce_id='
    data = fetch(query + sum_id).decode()
    content = json.loads(data)['html']
    doc = html.fromstring(content)
    summary = ''.join(map(extract_text, doc))
    #fix incorrectly  decoded numeric character representations ('&#xxx')
    fix = lambda match: bytes((ord(match.group()),)).decode('cp1251')
    return re.sub('[\x80-\xff]', fix, summary)


def get_schedule(channel, tz):
    ch_code = channel_code.get(channel)
    if ch_code is None:
        return []

    path = 'chanels/{0}/all/'.format(ch_code)

    doc = fromstring(fetch(path), parser)
    middle = doc[1][0][0][3][1][0][0][0]
    yellow_block = middle[0][0][0][0][1]
    ybcm = yellow_block[1][1][1]

    schedule = Schedule(tz, source_tz)
    summaries = {}

    d = monday
    for day in islice(ybcm, 2, None):
        schedule.set_date(d)
        for float in day[1]:
            for entry in float:
                schedule.set_time(entry[0].text)
                title = entry[1][0].text
                if title is not None:
                    schedule.set_title(title)
                onclick = entry.get('onclick')
                if onclick is not None:
                    sum_id = onclick[onclick.rfind(',') + 1: -1]
                    i = title.find('"')
                    if i >= 0:
                        title = title[i + 1: title.find('"', i + 1)]
                    summary = summaries.get(title)
                    if summary is None:
                        summary = get_summary(sum_id)
                        summaries[title] = summary
                    schedule.set_summary(summary)
        d += timedelta(1)

    return schedule.pop()
