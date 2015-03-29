import datetime
import pytz
import httplib2
import lxml.etree
from tv_schedule import schedule, dateutil


def need_channel_code():
    return False


_URL = 'http://pixelua.tv/category/tv-schedule/{}/'

_source_tz = pytz.timezone('Europe/Kiev')
_daydelta = datetime.timedelta(1)
_http = httplib2.Http()
_parser = lxml.etree.HTMLParser()


_weekadys = ['sunday', 'monday', 'tuesday', 'wednesday',
             'thursday', 'friday', 'saturday']

_implicit_fields = ['Оригінальна назва', 'Виробництво', 'Жанр',
                    'Про мультик', 'Про проект']


def _fetch(url):
    content = _http.request(url)[1]
    doc = lxml.etree.fromstring(content, _parser)
    return doc[1][10][1]


def _get_title_and_descr(url):
    left = _fetch(url)[0][1]
    title = left[0].text
    descr = ''
    field = None
    for child in left[1:]:
        tag = child.tag
        text = child.text if len(child) == 0 else child[0].text
        if tag == 'h3':
            field = child.text
            if field not in _implicit_fields:
                descr += text + ': '
        elif tag == 'ul':
            value = child[0].text
            if field == 'Оригінальна назва':
                title = value
            else:
                descr += value + '\n'
        elif text:
            descr += text + '\n'
    return title, descr


class _EventInfo:
    def __init__(self):
        self._cash = {}

    def get(self, a):
        href = a.get('href')
        key = href[href.rindex('/', 0, -1) + 1: -1]
        title, descr = self._cash.get(key) or (None, None)
        if title is None:
            self._cash[key] = title, descr = _get_title_and_descr(href)
        return title, descr


def get_schedule(channel, tz):
    if channel != 'Піксель':
        return []

    today = dateutil.tv_date_now(_source_tz)

    weekday_now = today.weekday()
    sched = schedule.Schedule(tz, _source_tz)

    event_info = _EventInfo()

    d = today
    for i in range(weekday_now, 7):
        sched.set_date(d)
        url = _URL.format(_weekadys[i])
        for li in _fetch(url)[3][0][1:]:
            sched.set_time(li[0].text)
            t = li[1]
            if len(t) == 0:
                title = t.text.strip()
                descr = None
            else:
                title, descr = event_info.get(t[0])
            sched.set_title(title)
            if descr:
                sched.set_descr(descr)
        d += _daydelta
    return sched.pop()
