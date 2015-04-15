import datetime
import urllib.parse
import pytz
import httplib2
import lxml.html
from tv_schedule import schedule, dateutil


def need_channel_code():
    return False

_url_map = {
    'Первый канал Европа': 'http://www.1tvrus.com',
    'Музыка Первого': 'http://www.muz1.tv/',
    'Дом кино': 'http://www.domkino.tv',
    'Время': 'http://www.vremya.tv/',
    'Телекафе': 'http://www.telecafe.ru/'
}

_URL = None
_PROG_URL = '/schedule/%Y-%m-%d'

_source_tz = pytz.timezone('Europe/Berlin')
_daydelta = datetime.timedelta(1)

_http = httplib2.Http()


def _fetch(url):
    url = urllib.parse.urljoin(_URL, url)
    content = _http.request(url)[1]
    doc = lxml.html.fromstring(content)
    return next(doc[1][2][0].iterchildren('div'))[1]


def _get_text(elem):
    return '\n'.join(x.text_content() for x in elem.iter('p'))


def _get_child_by_class(elem, cls):
    return next(x for x in elem if x.get('class') == cls)


def _get_descr(url):
    ann = _get_child_by_class(_fetch(url), 'announce_announce')
    descr = _get_text(ann[0][2])

    try:
        right = _get_child_by_class(ann[2], 'announce-view-service')
        descr += _get_text(right)
    except StopIteration:
        pass

    return descr


class _Descriptions:
    def __init__(self):
        self._cash = {}

    def get(self, a):
        href = a.get('href')
        spl = href.split('/')
        if spl[-2] == 'announce':
            key = int(spl[-1])
            descr = self._cash.get(key)
            if descr is None:
                self._cash[key] = descr = _get_descr(href)
            return descr


def get_schedule(channel, tz):
    global _URL

    _URL = _url_map.get(channel)
    if _URL is None:
        return []

    today = dateutil.tv_date_now(_source_tz, 5)
    weekday_now = today.weekday()
    sched = schedule.Schedule(tz, _source_tz)
    descriptions = _Descriptions()

    d = today
    for i in range(weekday_now, 7):
        sched.set_date(d)
        chan = _fetch(d.strftime(_PROG_URL))
        ul = chan[2][0][0][0][0][0][1][1]
        for li in (x for x in ul if len(x) > 0):
            div = li[0]
            sched.set_time(div[0].text)
            title = div[1]
            if len(title) == 0:
                sched.set_title(title.text.lstrip())
            else:
                a = title[0]
                sched.set_title(a.text)
                descr = descriptions.get(a)
                sched.set_descr(descr)
        d += _daydelta
    return sched.pop()
