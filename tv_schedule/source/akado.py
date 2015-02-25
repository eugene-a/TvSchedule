import datetime
import urllib.parse
import pytz
import httplib2
import lxml.etree

from tv_schedule import schedule, dateutil


def need_channel_code():
    return True

channel_code = None

_source_tz = pytz.timezone('Europe/Moscow')
_daydelta = datetime.timedelta(1)

_URL = 'http://tv.akado.ru/channels/'

_http = httplib2.Http()
_parser = lxml.etree.HTMLParser(encoding='utf-8')


def _fetch(url):
    url = urllib.parse.urljoin(_URL, url)
    content = _http.request(url)[1]
    tv_layout = lxml.etree.fromstring(content, _parser)[1][0][4]
    if tv_layout.get('class') is not None:
        return tv_layout[0][0]   # tv-common


def get_schedule(channel, tz):
    ch_code = channel_code.get(channel)
    if ch_code is None:
        return []

    today = dateutil.tv_date_now(_source_tz)
    weekday_now = today.weekday()

    sched = schedule.Schedule(tz, _source_tz)
    d = today

    for i in range(weekday_now, 7):
        sched.set_date(d)
        query = {'date': d.strftime('%Y-%m-%d')}
        url = ch_code + '.html?' + urllib.parse.urlencode(query)
        tv_common = _fetch(url)
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
