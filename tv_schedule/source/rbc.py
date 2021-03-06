import datetime
import pytz
import requests
import lxml.etree
from tv_schedule import schedule, dateutil


def need_channel_code():
    return False

_URL = 'http://rbctv.rbc.ru/tvprogram/%Y/%m/%d'

_source_tz = pytz.timezone('Europe/Moscow')
_daydelta = datetime.timedelta(1)

_parser = lxml.etree.HTMLParser(encoding='utf-8')


def _fetch(url):
    resp = requests.get(url)
    doc = lxml.etree.fromstring(resp.content, _parser)
    return doc[1][0][2][2][0][2][0][0]


def get_schedule(channel, tz):
    if channel != 'РБК':
        return []

    today = dateutil.tv_date_now(_source_tz, 0)
    weekday_now = today.weekday()
    sched = schedule.Schedule(tz, _source_tz)

    d = today
    for i in range(weekday_now, 7):
        sched.set_date(d)
        for row in _fetch(d.strftime(_URL)):
            sched.set_time(row[0].text)
            ev = row[1]
            title = ev.text
            a = ev[0]
            if title is None:
                title = a.text
            sched.set_title(title)
        d += _daydelta
    return sched.pop()
