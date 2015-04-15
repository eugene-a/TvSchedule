import itertools
import urllib.parse
import pytz
import httplib2
import lxml.etree
from tv_schedule import schedule, dateutil


def need_channel_code():
    return False

_source_tz = pytz.timezone('Europe/Moscow')
_URL = 'http://sovsekretno.tv/телепрограмма/'

_http = httplib2.Http()
_parser = lxml.etree.HTMLParser(encoding='utf-8')


def _fetch(url):
    content = _http.request(url)[1]
    doc = lxml.etree.fromstring(content, _parser)
    return doc[2][0][0][0][1][0]


def _get_descr(url):
    if urllib.parse.urlparse(url).path != '/':
        text = _fetch(url)[0][0][2][0][1][-2]
        return '\n'.join(x.text or '' for x in text)


class _Descriptions:
    def __init__(self):
        self._cash = {}

    def get(self, tooltip):
        if len(tooltip) == 0:
            return ''

        href = tooltip[0][0][-1][0].get('href')
        key = href[href.rindex('/', 0, -1) + 1: -1]
        descr = self._cash.get(key)
        if descr is None:
            self._cash[key] = descr = _get_descr(href) or ''
        return descr


def get_schedule(channel, tz):
    if channel != 'Совершенно секретно':
        return []

    descriptions = _Descriptions()
    sched = schedule.Schedule(tz, _source_tz)

    tabs = _fetch(_URL)[3]
    for day, tab in zip(tabs[0], tabs[2:]):
        a = day[0]
        date = a.text.strip() + ' ' + a[0].text.strip()
        sched.set_date(dateutil.parse_date(date, '%A %d %B'))
        for tv in itertools.chain(*(x[1:] for x in tab)):
            event = tv[0]
            sched.set_time(event[0].text)
            info = event[1]
            sched.set_title(info[1].text.lstrip())
            p = info[0]
            descr = (p.text.rstrip() + '\n' + p[0].text.strip() + '\n' +
                     descriptions.get(tv[1]))
            sched.set_descr(descr)
    return sched.pop()
