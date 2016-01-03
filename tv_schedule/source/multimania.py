import datetime
import urllib.parse
import pytz
import requests
import lxml.etree
from tv_schedule import schedule, dateutil


def need_channel_code():
    return False

_URL = 'http://www.multimania.tv/ru/guide/?'
_source_tz = pytz.timezone('Europe/Moscow')
_daydelta = datetime.timedelta(1)
_parser = lxml.etree.HTMLParser(encoding='utf-8')


def get_schedule(channel, tz):
    if channel != 'Мультимания':
        return []

    today = dateutil.tv_date_now(_source_tz)
    weekday_now = today.weekday()
    sched = schedule.Schedule(tz, _source_tz)

    d = today
    for i in range(weekday_now, 7):
        sched.set_date(d)
        resp = requests.get(_URL, {'d': d.strftime('%Y-%m-%d')})
        doc = lxml.etree.fromstring(resp.content, _parser)
        guide = doc[2][2][2][1][0][1][1][0][0]
        for row in guide[::2]:
            it = row.iterchildren()
            sched.set_time(next(it).text)
            sched.set_title(next(it)[0].text)
            sched.set_descr(row.getnext()[-1][0].text)
        d += _daydelta
    return sched.pop()
