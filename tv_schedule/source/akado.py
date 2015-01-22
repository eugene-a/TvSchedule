import datetime

import pytz
import httplib2
import lxml.etree

from tv_schedule import dateutil, schedule


def need_channel_code():
    return True

channel_code = None

_source_tz = pytz.timezone('Europe/Moscow')
_last_monday = dateutil.last_weekday(
    datetime.datetime.now(_source_tz).date(), 0)
_daydelta = datetime.timedelta(1)

_URL = 'http://tv.akado.ru/channels/'

_http = httplib2.Http()
_parser = lxml.etree.HTMLParser(encoding='utf-8')


def _fetch(path):
    content = _http.request(_URL + path)[1]
    tv_layout = lxml.etree.fromstring(content, _parser)[1][0][4]
    if tv_layout.get('class') is not None:
        return tv_layout[0][0]   # tv-common


def get_schedule(channel, tz):
    ch_code = channel_code.get(channel)
    if ch_code is None:
        return []

    sched = schedule.Schedule(tz, _source_tz)
    d = _last_monday

    for i in range(7):
        sched.set_date(d)
        path = ch_code + d.strftime('.html?date=%Y-%m-%d')
        tv_common = _fetch(path)
        if tv_common is None:
            break

        program = tv_common[1]

        for row in program.find('table'):    # tv-channel-full
            sched.set_time(row[0][0].text)
            cell = row[1]
            sched.set_title(cell[0].text)
            summary = cell[1].text
            if summary is not None:
                sched.set_summary(summary)

        d += _daydelta

    return sched.pop()
