import datetime
import pytz
import requests
import lxml.etree
from tv_schedule import schedule, dateutil


def need_channel_code():
    return False

_URL = 'http://u-tv.ru/tv/'
_source_tz = pytz.timezone('Europe/Moscow')
_daydelta = datetime.timedelta(1)
_parser = lxml.etree.HTMLParser()


def get_schedule(channel, tz):
    if channel != 'Ю':
        return []

    today = dateutil.tv_date_now(_source_tz, 5)
    weekday_now = today.weekday()
    sched = schedule.Schedule(tz, _source_tz)

    d = today
    for i in range(weekday_now, 7):
        sched.set_date(d)
        param = {'date': d.strftime('%Y-%m-%d')}
        resp = requests.get(_URL, param)
        doc = lxml.etree.fromstring(resp.content, _parser)
        wrapper = doc[1][5][0][0][0][13]
        if wrapper.tag != 'div':
            wrapper = wrapper.getnext()
        for event in wrapper[0][0][0][0][1][1]:
            it = event.iterchildren()
            sched.set_time(next(it).text)
            next(it)
            it = next(it).iterdescendants()
            next(it)
            sched.set_title(next(it).text)
            try:
                descr = next(it).text + ' ' + next(it).text
                sched.set_descr(descr)
            except StopIteration:
                pass
        d += _daydelta
    return sched.pop()
