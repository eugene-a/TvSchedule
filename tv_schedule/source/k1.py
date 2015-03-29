import datetime
import urllib.parse
import pytz
import httplib2
import lxml.html
from tv_schedule import schedule, dateutil


def need_channel_code():
    return False

_URL = 'http://www.k1.ua'
_SCHED_URL = '/{}/tv/%Y/%m/%d/week'
_source_tz = pytz.timezone('Europe/Kiev')
_http = httplib2.Http()


def _week_monday(d):
    return d - datetime.timedelta(d.weekday())

_last_monday = _week_monday(dateutil.tv_date_now(_source_tz))

_sched_url = _last_monday.strftime(_SCHED_URL)


def child_by_class(el, cls):
    return next(
        x for x in el.iterchildren('div') if cls in x.get('class').split()
    )


def _fetch(url):
    url = urllib.parse.urljoin(_URL, url)
    content = _http.request(url)[1]
    doc = lxml.html.fromstring(content)
    holder = child_by_class(doc[1], 'b-holder')
    return child_by_class(holder[10][0], 'b-inside-left')


def _get_sched(lang):
    url = _sched_url.format(lang)
    return _fetch(url)[0][1][3]


def _get_descr(url):
    inside_left = _fetch(url)
    if inside_left[0].get('class') == 'b-404-error':
        return ''
    else:
        block_body = child_by_class(inside_left, 'b-block-body')
        text = block_body[0][1][0]
        return '\n'.join(x.text_content() or '' for x in text)


class _Descriptions:
    def __init__(self):
        self._cash = {}

    def get(self, a):
        href = a.get('href')
        if len(href) > 4:
            if href.count('/') > 4:
                descr = _get_descr(href)
            else:
                key = href[href.rindex('/') + 1:]
                descr = self._cash.get(key)
                if descr is None:
                    self._cash[key] = descr = _get_descr(href)
            return descr


def get_schedule(channel, tz):
    if channel != 'К1':
        return []

    sched = schedule.Schedule(tz, _source_tz)
    descriptions = _Descriptions()

    tables = (x[0][0] for x in _get_sched('uk')[2::5])
    for info, events in zip(_get_sched('ru')[::5], tables):
        d = dateutil.parse_date(info[0][-1].text, '%A, %d %B')
        sched.set_date(d)
        for event in events:
            it = event.iterchildren()
            sched.set_time(next(it)[0].text)
            a = next(it)[0]
            sched.set_title(a.text)
            descr = descriptions.get(a)
            if descr:
                sched.set_descr(descr)
    return sched.pop()
