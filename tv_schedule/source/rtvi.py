import urllib.parse
import datetime
import pytz
import requests
import lxml.html
from tv_schedule import schedule, dateutil


def need_channel_code():
    return False


_URL = 'http://www.rtvi.com/programma/%Y/%m/%d'

_source_tz = pytz.timezone('CET')
_daydelta = datetime.timedelta(1)
_parser = lxml.html.HTMLParser(encoding='utf-8')


def get_schedule(channel, tz):
    if channel != 'RTVi':
        return []

    today = dateutil.tv_date_now(_source_tz, 8)

    weekday_now = today.weekday()
    sched = schedule.Schedule(tz, _source_tz)

    session = requests.session()
    param = {'setregion': 43291}

    d = today
    for i in range(weekday_now, 7):
        sched.set_date(d)
        resp = session.get(d.strftime(_URL), params=param)
        param = None
        doc = lxml.html.fromstring(resp.content, parser=_parser)
        ul = doc[1][10][1][2][1][0][2]
        popups = ul.getnext()
        for ev in ul:
            a = ev[0]
            if a.tag != 'a':
                descr = None
            else:
                popup = popups.get_element_by_id(a.get('href')[1:])
                descr = '\n'.join(x.text or ''
                                  for x in popup.iterchildren('p'))
                ev = a

            it = ev.iterchildren()
            sched.set_time(next(it).text, next(it).text == 'PM')
            sched.set_title(next(it).text_content())
            if descr:
                sched.set_descr(descr)
        d += _daydelta
    return sched.pop()
