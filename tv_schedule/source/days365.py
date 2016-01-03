import datetime
import pytz
import requests
import lxml.html
from tv_schedule import schedule


def need_channel_code():
    return False

_URL = 'http://www.365days.ru/teleprogram'
_source_tz = pytz.timezone('Europe/Moscow')


def _fetch(url):
    resp = requests.get(url)
    doc = lxml.html.fromstring(resp.content)
    return doc[1][0][0][0][0][3][0][0][0]


def _get_descr(url):
    descr = ''
    for p in _fetch(url)[1].iterchildren('p'):
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
        dt = datetime.datetime.strptime(tab.get('data-day'), 'tv_%Y%m%d')
        sched.set_date(dt.date())
        for period in tab[0]:
            for event in period[1:]:
                it = event.iterdescendants()
                next(it)
                sched.set_time(next(it).text)
                next(it)
                next(it)
                a = next(it)
                if a.tag == 'a':
                    sched.set_title(a.text)
                    sched.set_descr(descriptions.get(a))
                else:
                    sched.set_title(next(it).text)
                    sched.set_descr(next(it).text)

    return sched.pop()
