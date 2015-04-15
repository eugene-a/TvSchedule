import datetime
import pytz
import httplib2
import lxml.etree
from tv_schedule import schedule, dateutil


def need_channel_code():
    return False

_source_tz = pytz.timezone('Europe/Moscow')
_URL = 'http://www.universalchannel.ru/schedule/%Y-%m-%d'

_daydelta = datetime.timedelta(1)
_http = httplib2.Http()
_parser = lxml.etree.HTMLParser()


def get_schedule(channel, tz):
    if channel != 'Universal Channel':
        return []

    today = dateutil.tv_date_now(_source_tz)
    weekday_now = today.weekday()
    sched = schedule.Schedule(tz, _source_tz)

    d = today
    for i in range(weekday_now, 7):
        sched.set_date(d)

        url = d.strftime(_URL)
        content = _http.request(url)[1]
        doc = lxml.etree.fromstring(content, _parser)
        zoo = doc[2][8]
        inner = doc[2][7][0][0][2][0][0][0][0][0][1][0]

        for event in (x for x in inner[2:] if len(x) > 1):
            sched.set_time(event[0].text)
            info = event[1]
            title = info[0]
            sched.set_title(title.text or title[0].text)
            descr = ' '.join(info[1].text.split())
            descr = descr + '\n' if descr else ''
            sched.set_descr(descr + info[2][0].text.strip())
        d += _daydelta
    return sched.pop()
