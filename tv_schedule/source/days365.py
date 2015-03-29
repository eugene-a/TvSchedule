import datetime
import pytz
import httplib2
import lxml.html
from tv_schedule import schedule, dateutil


def need_channel_code():
    return False

_URL = 'http://www.365days.ru/teleprogram'
_source_tz = pytz.timezone('Europe/Moscow')
_http = httplib2.Http()


def _fetch(url):
    content = _http.request(url)[1]
    doc = lxml.html.fromstring(content)
    return doc[1][0][0][0][0][3][0][0][0]


def _get_descr(url):
    descr = ''
    for p in _fetch(url).iterchildren('p'):
        for br in p.iterchildren('br'):
            br.tail = '\n' + (br.tail or '')
        descr += p.text_content() + '\n'
    return descr


class _Descriptions:
    def __init__(self):
        self._cash = {}

    def get(self, a):
        href = a.get('href')
        key = int(href[href.rindex('/', 0, -1) + 1: -1])
        descr = self._cash.get(key)
        if descr is None:
            self._cash[key] = descr = _get_descr(href)
        return descr


def get_schedule(channel, tz):
    if channel != '365 дней ТВ':
        return []

    sched = schedule.Schedule(tz, _source_tz)
    descriptions = _Descriptions()

    for tab in _fetch(_URL)[4][4: 11]:
        dt = datetime.datetime.strptime(tab.get('rel'), 'tv_%Y%m%d')
        sched.set_date(dt.date())
        for event in tab[0]:
            it = event.iterchildren()
            sched.set_time(next(it).text)
            span = next(it)
            if len(span) < 2:
                sched.set_title(span.text.lstrip())
            else:
                a = next(span.iterchildren('a', reversed=True))
                sched.set_title(a.text.rstrip(','))
                sched.set_descr(descriptions.get(a))
    return sched.pop()
