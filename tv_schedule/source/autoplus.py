import datetime
import pytz
import requests
import lxml.etree
from tv_schedule import schedule


def need_channel_code():
    return False

_URL = 'http://www.autoplustv.ru/teleprogram'
_source_tz = pytz.timezone('Europe/Moscow')
_daydelta = datetime.timedelta(1)
_parser = lxml.etree.HTMLParser()


def _fetch(url):
    resp = requests.get(url)
    doc = lxml.etree.fromstring(resp.content, _parser)
    return doc[1][0][0][0][0][3][0][0]


def _get_descr(url):
    title = next(_fetch(url).iterchildren('div'))[0]
    return (title.tail or '') + '\n'.join(x.text or ''
                                          for x in title.itersiblings('p'))


class _Descriptions:
    def __init__(self):
        self._cash = {}

    def get(self, a):
        href = a.get('href')
        key = int(href[href.rindex('/') + 1:])
        descr = self._cash.get(key)
        if descr is None:
            self._cash[key] = descr = _get_descr(href)
        return descr


def get_schedule(channel, tz):
    if channel != 'Авто плюс':
        return []

    sched = schedule.Schedule(tz, _source_tz)
    descriptions = _Descriptions()

    for tab in _fetch(_URL)[0][2][4: -1]:
        d = datetime.datetime.strptime(tab.get('data-day'), 'tv_%Y%m%d').date()
        sched.set_date(d)
        for period in tab[0]:
            for event in period[1:]:
                sched.set_time(event[0][0].text)
                dd = event[1]
                it = dd.iterdescendants()
                next(it)
                a = next(it)
                if a.tag == 'a':
                    sched.set_title(a.text)
                    sched.set_descr(descriptions.get(a))
                else:
                    sched.set_title(next(it).text)
                    sched.set_descr(next(it).text)

    return sched.pop()
