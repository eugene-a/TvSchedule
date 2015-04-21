import datetime
import pytz
import httplib2
import lxml.html
from tv_schedule import schedule, dateutil


def need_channel_code():
    return False

_source_tz = pytz.timezone('Europe/Kiev')
_URL = 'http://footballua.tv/schedule/single/schedule_f{}/%d-%m-%Y'

_http = httplib2.Http()
_daydelta = datetime.timedelta(1)

_parser = lxml.html.HTMLParser(encoding='utf-8')

def get_schedule(channel, tz):
    if channel not in ('Футбол 1', 'Футбол 2'):
        return []

    url = _URL.format(channel[-1])

    today = dateutil.tv_date_now(_source_tz)
    weekday_now = today.weekday()
    sched = schedule.Schedule(tz, _source_tz)

    d = today
    for i in range(weekday_now, 7):
        sched.set_date(d)
        content = _http.request(d.strftime(url))[1]
        doc = lxml.etree.fromstring(content, parser=_parser)
        for row in doc[0][0][0][::2]:
            table = row[0][0]
            tr = table[0]
            sched.set_time(tr[0][0][0].text)
            sched.set_title(tr[1][0][0][0].text_content())
            sched.set_descr(table[2][0][0][0].text)
        d += _daydelta
    return sched.pop()
