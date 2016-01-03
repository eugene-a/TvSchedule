import datetime
import urllib.parse
import pytz
import requests
import lxml.etree

from tv_schedule import schedule, dateutil


def need_channel_code():
    return True

channel_code = None

_source_tz = pytz.timezone('Europe/Moscow')
_daydelta = datetime.timedelta(1)

_URL = 'http://tv.akado.ru/channels/'

_parser = lxml.etree.HTMLParser(encoding='utf-8')


def _fetch(url, params=None):
    url = urllib.parse.urljoin(_URL, url)
    resp = requests.get(url, params)
    tv_layout = lxml.etree.fromstring(resp.content, _parser)[1][0][4]
    if tv_layout.get('class') is not None:
        return tv_layout[0][0]   # tv-common


def get_schedule(channel, tz):
    ch_code = channel_code.get(channel)
    if ch_code is None:
        return []

    today = dateutil.tv_date_now(_source_tz, 5)
    weekday_now = today.weekday()

    sched = schedule.Schedule(tz, _source_tz)
    d = today

    for i in range(weekday_now, 7):
        sched.set_date(d)
        param = {'date': d.strftime('%Y-%m-%d')}
        tv_common = _fetch(ch_code + '.html', param)
        if tv_common is None:
            break

        program = tv_common[1]

        for row in program.find('table'):    # tv-channel-full
            sched.set_time(row[0][0].text)
            cell = row[1]
            sched.set_title(cell[0].text)
            descr = cell[1].text
            if descr is not None:
                sched.set_descr(descr)

        d += _daydelta

    return sched.pop()
