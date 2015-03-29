import datetime
import pytz
import httplib2
import lxml.html
from tv_schedule import schedule, dateutil


def need_channel_code():
    return False

_URL = 'http://www.rtvi.com/programma/%Y/%m/%d?setregion=2'

_source_tz = pytz.timezone('Europe/Moscow')
_daydelta = datetime.timedelta(1)
_http = httplib2.Http()
_parser = lxml.html.HTMLParser(encoding='utf-8')


def get_schedule(channel, tz):
    if channel != 'RTVi':
        return []

    today = dateutil.tv_date_now(_source_tz, 8)

    weekday_now = today.weekday()
    sched = schedule.Schedule(tz, _source_tz)

    d = today
    for i in range(weekday_now, 7):
        sched.set_date(d)
        content = _http.request(d.strftime(_URL))[1]
        doc = lxml.html.fromstring(content, parser=_parser)
        ul = doc[1][10][1][2][1][0][2]
        popups = ul.getnext()
        for ev in ul:
            a = ev[0]
            if a.tag != 'a':
                descr = None
            else:
                popup = popups.get_element_by_id(a.get('href')[1:])
                descr = '\n'.join(x.text for x in popup.iterchildren('p'))
                ev = a

            it = ev.iterchildren()
            sched.set_time(next(it).text, next(it).text == 'PM')
            sched.set_title(next(it).text_content())
            if descr:
                sched.set_descr(descr)
        d += _daydelta
    return sched.pop()
