import datetime
import urllib.parse
import itertools
import pytz
import httplib2
import lxml.html
from tv_schedule import schedule, dateutil


def need_channel_code():
    return False


_url_map = {
    'ТНТ': 'http://tvprogram.tnt-online.ru',
    'ТНТ-Comedy': 'http://tnt-online.ru/tnt-comedy-tv/russia/tvprogram/'
}

_URL = None


_source_tz = pytz.timezone('Europe/Moscow')
_daydelta = datetime.timedelta(1)

_http = httplib2.Http()


def _fetch(url):
    content = _http.request(url)[1]
    doc = lxml.html.fromstring(content)
    return doc[1][2][3]


def _get_text(elem):
    return '\n'.join(x.text_content() for x in elem.iterchildren('div'))


def _get_descr(url):
    center = _fetch(url).get_element_by_id('center-block')
    if center is not None:
        info = next(itertools.islice(center.iterchildren('div'), 1, None))
        return _get_text(info[0][0][0])


class _Descriptions:
    def __init__(self):
        self._cash = {}

    def get(self, a):
        if a.tag == 'a':
            href = a.get('href')
            key = href[href.rindex('/') + 1:]
            descr = self._cash.get(key)
            if descr is None:
                self._cash[key] = descr = _get_descr(href)
            return descr


def get_schedule(channel, tz):
    global _URL

    _URL = _url_map.get(channel)
    if _URL is None:
        return []

    today = dateutil.tv_date_now(_source_tz)
    weekday_now = today.weekday()
    sched = schedule.Schedule(tz, pytz.timezone('UTC'))

    descriptions = _Descriptions()

    d = today
    for i in range(weekday_now, 7):
        url = urllib.parse.urljoin(_URL, d.strftime('%Y-%m-%d.htm'))
        for dl in _fetch(url).get_element_by_id('tv-list-item')[1:]:
            dt = datetime.datetime.utcfromtimestamp(int(dl.get('time')))
            sched.set_datetime(dt)
            dd = dl[-1]
            t1 = next(x for x in dd.iterchildren()
                      if x.get('class') != 'tv-preview')
            t2 = t1.getnext()
            if t2 is None:
                sched.set_title(t1.text)
            else:
                sched.set_title(t1.text + ' ' + t2.text)
                t3 = next(t2.itersiblings('div'), None)
                descr = t3.text + '\n' if t3 is not None else ''
                descr += descriptions.get(t2) or ''
                sched.set_descr(descr)
        d += _daydelta
    return sched.pop()
