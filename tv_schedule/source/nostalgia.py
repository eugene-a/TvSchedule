import datetime
import re
import urllib.parse
import pytz
import httplib2
import lxml.etree
from tv_schedule import schedule, dateutil


def need_channel_code():
    return False

_source_tz = pytz.timezone('Europe/Moscow')
_URL = 'http://www.nostalgiatv.ru/programs?'

_daydelta = datetime.timedelta(1)
_http = httplib2.Http()
_parser = lxml.etree.HTMLParser()


def get_schedule(channel, tz):
    if channel != 'Ностальгия':
        return []

    sched = schedule.Schedule(tz, _source_tz)

    today = dateutil.tv_date_now(_source_tz, 6)
    weekday_now = today.weekday()
    sched = schedule.Schedule(tz, _source_tz)
    rex = re.compile('([0-9]+\+ )([^\.«»]*(?:«.+»)?[^\.«»]*\.?)(.*)')

    d = today
    for i in range(weekday_now, 7):
        sched.set_date(d)
        query = urllib.parse.urlencode({'day': d.strftime('%Y-%m-%d')})
        content = _http.request(_URL + query)[1]
        doc = lxml.etree.fromstring(content, _parser)
        table = doc[1][2][0][0][11][6]
        for row in table:
            sched.set_time(row[0][0][0].text)
            m = rex.match(row[1].text)
            age, title, descr = m.groups()
            sched.set_title(title)
            sched.set_descr(age + descr)
        d += _daydelta
    return sched.pop()
