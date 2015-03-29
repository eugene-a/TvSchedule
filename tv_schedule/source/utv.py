import datetime
import urllib.parse
import pytz
import httplib2
import lxml.etree
from tv_schedule import schedule, dateutil


def need_channel_code():
    return False

_URL = 'http://u-tv.ru/tv/?'
_source_tz = pytz.timezone('Europe/Moscow')
_daydelta = datetime.timedelta(1)
_http = httplib2.Http()
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
        query = {'date': d.strftime('%Y-%m-%d')}
        url = _URL + urllib.parse.urlencode(query)
        content = _http.request(url)[1]
        doc = lxml.etree.fromstring(content, _parser)
        for event in doc[1][6][0][0][0][7][4][0][0][0][1][1: -1]:
            it = event.iterchildren()
            sched.set_time(next(it).text)
            next(it)
            it = next(it).iterdescendants()
            next(it)
            next(it)
            sched.set_title(next(it).text)
            descr = next(it).text + ' ' + next(it).text
            sched.set_descr(descr)
        d += _daydelta
    return sched.pop()
