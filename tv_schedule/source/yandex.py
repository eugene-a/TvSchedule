import datetime
import urllib.parse
import json
import lxml.etree
import requests
from tv_schedule import dateutil, schedule


def need_channel_code():
    return True

channel_code = None

_URL = 'https://tv.yandex.ru'
_CLS_DETAILS = 'b-tv-program-details'
_CLS_DESCR = 'b-tv-program-description'

_parser = lxml.etree.HTMLParser(encoding='utf-8')

_daydelta = datetime.timedelta(1)

_RETRY_COUNT = 5


def _fetch(url, params=None):
    url = urllib.parse.urljoin(_URL, url)
    resp = requests.get(url, params)
    content = resp.content
    if len(content) > 0:
        # retry in the case of gateway timeout
        for i in range(_RETRY_COUNT):
            doc = lxml.etree.fromstring(content, _parser)
            cont = doc[1][0]
            if cont.tag == 'div':
                return cont[2][0]


def get_descr(a):
    content = _fetch(a.get('href'))
    td = content[1][0][0]

    descr = ''
    d = next((x for x in td if x.get('class') == _CLS_DETAILS), None)
    if d is not None:
        for row in d[0]:
            descr += row[0].text + ' '
            val = row[1]
            descr += val.text or val[0].text
            descr += '\n'
        dnext = d.getnext()
        if dnext is not None and dnext.get('class') == _CLS_DESCR:
            ds = dnext[0]
            descr += ds[0].text
            if len(ds) > 1:
                descr += ' '
                dc = json.loads(ds[1].get('data-bem'))
                descr += dc['b-tv-cut-button']['content'][0]['content']
            descr += '\n'
    return descr


class _EventInfo:
    def __init__(self):
        self._cash = {}

    def get(self, a):
        title = a[1].text or a[1][0].text
        descr = self._cash.get(title)
        if descr is None:
            self._cash[title] = descr = get_descr(a)
        return title, descr


def get_schedule(channel, tz):
    ch_code = channel_code.get(channel)
    if ch_code is None:
        return []

    today = dateutil.tv_date_now(tz)
    weekday_now = today.weekday()

    sched = schedule.Schedule(tz, tz)
    event_info = _EventInfo()
    d = today
    for i in range(weekday_now, 7):
        sched.set_date(d)
        url = '/87/channels/' + ch_code
        content = _fetch(url, {'date': d.strftime('%Y-%m-%d')})
        if content is not None:
            items = content[2][0][0][0][0][0][0]
            if items.get('class') != 'tv-splash':
                for item in items:
                    a = item[0]
                    sched.set_time(a[0].text)
                    title, descr = event_info.get(a)
                    sched.set_title(title)
                    if descr:
                        sched.set_descr(descr)
        d += _daydelta
    return sched.pop()
