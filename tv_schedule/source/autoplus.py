import datetime
import pytz
import httplib2
import lxml.etree
from tv_schedule import schedule, dateutil


def need_channel_code():
    return False

_URL = 'http://www.autoplustv.ru/teleprogram'
_SCHED_URL = '/schedule/?'
_source_tz = pytz.timezone('Europe/Moscow')
_daydelta = datetime.timedelta(1)
_http = httplib2.Http()
_parser = lxml.etree.HTMLParser()


def _fetch(url):
    content = _http.request(url)[1]
    doc = lxml.etree.fromstring(content, _parser)
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

    buttons = _fetch(_URL)[2][2][3]
    dates = (dateutil.parse_date(x.text, '%a %d.%m') for x in buttons[0])
    for d, tab in zip(dates, buttons.itersiblings()):
        sched.set_date(d)
        for event in tab[0]:
            sched.set_time(event[0].text)
            span = event[1]
            if len(span) < 2:
                sched.set_title(span.text.lstrip())
            else:
                a = next(span.iterchildren('a', reversed=True))
                sched.set_title(a.text)
                sched.set_descr(descriptions.get(a))

    return sched.pop()
