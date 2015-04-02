import httplib2
import lxml.etree
import pytz

from tv_schedule import dateutil, schedule


def need_channel_code():
    return True

channel_code = None

_URL = ('http://www.viasat.lv/viasat0/tv-programma27/tv-programma28/' +
        '_/all/0/{}/?viewweek=1')

_source_tz = pytz.timezone('Europe/Riga')

_http = httplib2.Http()
_parser = lxml.etree.HTMLParser()


def get_schedule(channel, tz):
    ch_code = channel_code.get(channel)
    if ch_code is None:
        return []

    sched = schedule.Schedule(tz, _source_tz)

    url = _URL.format(ch_code)
    doc = lxml.etree.fromstring(_http.request(url)[1], _parser)
    prog = doc[1][0][5][0][3][0][1][0]

    new_date = False
    for div in prog[0][1]:
        if len(div) == 0:
            new_date = True
        elif new_date:
            new_date = False
            date_str = div[0][0][1][0].text
            date = dateutil.parse_date(date_str, '%a, %d. %b')
            sched.set_date(date)
        else:
            sched.set_time(div[0].text)
            h3 = div[-1][-3][0]
            if len(h3) == 0:
                title = h3.text
            else:
                sched.set_foreign_title()
                title = h3[0].text
                title = title[1: -1]
            sched.set_title(title.rstrip())
            sched.set_descr(h3.tail)
    return sched.pop()
