import datetime
import urllib.parse
import pytz
import requests
import lxml.etree
from tv_schedule import schedule, dateutil


def need_channel_code():
    return False

_URL = 'http://novy.tv/tv/{}/'
_source_tz = pytz.timezone('Europe/Kiev')
_daydelta = datetime.timedelta(1)
_parser = lxml.etree.HTMLParser(encoding='utf-8')

_weekdays = ['monday', 'tuesday', 'wednesday', 'thursday',
             'friday', 'saturday', 'sunday']


def _fetch(url):
    resp = requests.get(url)
    doc = lxml.etree.fromstring(resp.content, _parser)
    return doc[1][9][0][3]


def _get_descr(url):
    try:
        cont = _fetch(url)[1][0][0][1][1]
        return '\n'.join(x.text or '' for x in cont[1:])
    except IndexError:
        return ''


class _Descriptions:
    def __init__(self):
        self._cash = {}

    def get(self, a):
        href = a.get('href')
        path = urllib.parse.urlparse(href).path
        if path != '':
            key = href[href.rindex('/', 0, -1) + 1: -1]
            descr = self._cash.get(key)
            if descr is None:
                self._cash[key] = descr = _get_descr(href)
            return descr


def get_schedule(channel, tz):
    if channel != 'Новый канал':
        return []

    today = dateutil.tv_date_now(_source_tz)
    weekday_now = today.weekday()
    sched = schedule.Schedule(tz, _source_tz)
    descriptions = _Descriptions()
    d = today
    for i in range(weekday_now, 7):
        sched.set_date(d)
        url = _URL.format(_weekdays[i])
        day = _fetch(url)[0][0][0][0][1][0][1][0]
        for a in (x[0] for x in day if len(x) > 0):
            sched.set_time(a[0].text)
            title = a[2].text
            descr = descriptions.get(a) or a.getnext()[0][3].text.strip()
            if title is None and descr:
                title, descr = descr.split(' - ', 1)
            if title:
                sched.set_title(title)
                sched.set_descr(descr)
        d += _daydelta
    return sched.pop()
