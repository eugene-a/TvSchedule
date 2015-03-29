import datetime
import urllib.parse
import pytz
import httplib2
import lxml.html
from tv_schedule import schedule, dateutil


def need_channel_code():
    return False

_URL = 'http://www.karusel-tv.ru'
_SCHED_URL = '/schedule/%Y-%m-%d'
_source_tz = pytz.timezone('Europe/Moscow')
_daydelta = datetime.timedelta(1)
_http = httplib2.Http()


def _fetch(url):
    url = urllib.parse.urljoin(_URL, url)
    content = _http.request(url)[1]
    doc = lxml.html.fromstring(content)
    return doc[1][0][0][-1]


def _get_text(el):
    return '/n'.join(x.text_content() for x in el.iterchildren('p'))


def _get_descr(url):
    content = _fetch(url)
    block = next(content.iterchildren('input')).getnext()
    left = block[0][1][0][0]
    descr = left[0][1].text + '\n'
    for child in left.getnext()[1:]:
        cls = child.get('class')
        if cls == 'full':
            descr += _get_text(child)
            creators = child[-1]
            if creators.get('class') == 'announce-creators':
                descr += creators[1][0].text_content()
        elif cls == 'announce-creators':
            descr += child[1][0].text_content()
        elif len(child) > 0:
            descr += _get_text(child)
        elif child.text:
            descr += child.text + '\n'
    return descr


class _Descriptions:
    def __init__(self):
        self._cash = {}

    def get(self, a):
        href = urllib.parse.urlparse(a.get('href')).path
        key = int(href[href.rindex('/') + 1:])
        descr = self._cash.get(key)
        if descr is None:
            self._cash[key] = descr = _get_descr(href)
        return descr


def get_schedule(channel, tz):
    if channel != 'Карусель':
        return []

    today = dateutil.tv_date_now(_source_tz)
    weekday_now = today.weekday()
    sched = schedule.Schedule(tz, _source_tz)
    descriptions = _Descriptions()

    d = today
    for i in range(weekday_now, 7):
        sched.set_date(d)
        url = d.strftime(_SCHED_URL)
        grid = _fetch(url)[0][0][1][6]
        for li in (x for x in grid[1:] if len(x) > 0):
            span = li[0][0][0][0]
            sched.set_time(span.text)
            a = span.getnext()
            if a.tag != 'a':
                sched.set_title(a.text)
                sched.set_descr(a.getnext().text)
            else:
                sched.set_title(a[1].text)
                descr = a[2].text + '\n' + descriptions.get(a)
                sched.set_descr(descr)
        d += _daydelta
    return sched.pop()
