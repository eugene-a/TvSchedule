import datetime
import urllib.parse
import pytz
import httplib2
import lxml.html
from tv_schedule import schedule, dateutil


def need_channel_code():
    return False

_URL = 'http://inter.ua'
_SCHED_URL = '/ru/tv/%Y/%m/%d'
_source_tz = pytz.timezone('Europe/Kiev')
_daydelta = datetime.timedelta(1)
_http = httplib2.Http()
_parser = lxml.etree.HTMLParser()


def _fetch(url):
    url = urllib.parse.urljoin(_URL, url)
    content = _http.request(url)[1]
    doc = lxml.etree.fromstring(content, _parser)
    return doc[1][-16][0][0][3][0][0]


def _get_descr(url):
    descr = ''
    inside = _fetch(url)
    info = inside[1][0]
    if len(info) > 2:
        for dt in info[2][0][::2]:
            field = dt.text
            if field in ('Режиссер:', 'В ролях:'):
                descr += field + ' '
            descr += dt.getnext().text + '\n'
    static = inside.find('.//div[@class="b-static-text"]')
    descr += '\n'.join(x.text if x.text else '' for x in static)
    return descr


class _Descriptions:
    def __init__(self):
        self._cash = {}

    def get(self, a):
        href = a.get('href')
        key = href[href.rindex('/') + 1:]
        descr = self._cash.get(key)
        if descr is None:
            self._cash[key] = descr = _get_descr(href)
        return descr


def get_schedule(channel, tz):
    if channel != 'Интер':
        return []

    today = dateutil.tv_date_now(_source_tz)
    weekday_now = today.weekday()
    sched = schedule.Schedule(tz, _source_tz)
    descriptions = _Descriptions()

    d = today
    for i in range(weekday_now, 7):
        sched.set_date(d)
        dl = _fetch(d.strftime(_SCHED_URL))[1][0][4]
        for dt in (x for x in dl[1:] if x.tag == 'dt'):
            sched.set_time(dt.text)
            dd = dt.getnext()
            if len(dd) == 0:
                sched.set_title(dd.text)
            else:
                a = dd[-1]
                sched.set_title(a.text)
                sched.set_descr(descriptions.get(a))
        d += _daydelta
    return sched.pop()
