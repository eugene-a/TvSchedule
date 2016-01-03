import datetime
import pytz
import requests
import lxml.html
from tv_schedule import schedule


def need_channel_code():
    return False

_URL = 'http://www.serialtv.ru/teleprogram/'
_source_tz = pytz.timezone('Europe/Moscow')


def _fetch(url):
    resp = requests.get(url)
    doc = lxml.html.fromstring(resp.content)
    return doc[1][0][0][2][0][0][0][0]


def _get_text(p):
    for br in p.iterdescendants('br'):
        br.tail = '\n' + (br.tail or '')
    return p.text_content()


def _get_descr(url):
    body = _fetch(url)[1]
    return '\n'.join(_get_text(x) for x in body[2: -1])


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
    if channel != 'Много ТВ':
        return []

    sched = schedule.Schedule(tz, _source_tz)
    descriptions = _Descriptions()

    teleprog = _fetch(_URL)[0][1][0][1]
    for tab in teleprog[4: 11]:
        dt = datetime.datetime.strptime(tab.get('data-day'), 'tv_%Y%m%d')
        sched.set_date(dt.date())
        for event in tab[0]:
            it = event.iterchildren()
            sched.set_time(next(it).text)
            span = next(it)
            if len(span) < 2:
                title = span.text.lstrip()
                descr = span[0].text
            else:
                a = span[0]
                if span[1].tag == 'span':
                    title = span[1][1].text
                else:
                    title = a.text or span[2].text
                descr = descriptions.get(a)
            sched.set_title(title)
            sched.set_descr(descr)
    return sched.pop()
