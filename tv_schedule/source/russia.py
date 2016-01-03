import datetime
import urllib.parse
import itertools
import requests
import pytz
import lxml.html
from tv_schedule import schedule, dateutil


def need_channel_code():
    return False

_russia_tz = pytz.timezone('Europe/Moscow')
_europe_tz = pytz.timezone('Europe/Berlin')

_channels = {
    'Россия': ('http://russia.tv', _russia_tz),
    'РТР-Планета': ('http://rtr-planeta.com', _europe_tz),
    'Россия 2': ('http://2.russia.tv', _russia_tz),
    'Культура': ('http://tvkultura.ru', _russia_tz)
}

_URL = None
_PROG_URL = '/tvp/index/date/%d-%m-%Y'

_daydelta = datetime.timedelta(1)

_parser = lxml.html.HTMLParser(encoding='utf-8')


def _fetch(url):
    url = urllib.parse.urljoin(_URL, url)
    resp = requests.get(url)
    doc = lxml.html.fromstring(resp.content, parser=_parser)
    try:
        main = doc.get_element_by_id('main')
    except KeyError:
        pass
    else:
        return main[0]


def _get_descr(url):
    cont = _fetch(url)
    if cont is not None and cont.get('id') == 'blocks':
        try:
            b = next(
                (x for x in cont if x.get('data-block_id') == 'about_full')
            )
        except StopIteration:
            pass
        else:
            return b[1][0].text_content().replace('\t', '')


class _Descriptions:
    def __init__(self):
        self._cash = {}

    def get(self, a):
        url = a.get('href')
        # make sure it's a relative url
        if urllib.parse.urlsplit(url).scheme == '':
            key = int(url[url.rindex('/', 0,  -1) + 1: -1])
            descr = self._cash.get(key)
            if descr is None:
                self._cash[key] = descr = _get_descr(url) or ''
            return descr


def get_schedule(channel, tz):
    global _URL

    _URL, source_tz = _channels.get(channel) or (None, None)
    if _URL is None:
        return []

    descriptions = _Descriptions()

    today = dateutil.tv_date_now(source_tz)
    weekday_now = today.weekday()
    sched = schedule.Schedule(tz, source_tz)

    d = today
    for i in range(weekday_now, 7):
        sched.set_date(d)
        content = _fetch(d.strftime(_PROG_URL))
        tvp_day = next(itertools.islice(content.iterchildren('div'), 1, 2))
        for li in tvp_day[0][1][0]:
            try:
                a = next(li[1].iter('a'))
                t = li[0]
                time = t.text if len(t) == 0 else t[0].text
                sched.set_time(time)
                sched.set_title(a[0].text.lstrip())
                descr = descriptions.get(a)
                if descr:
                    sched.set_descr(descr)
            except StopIteration:
                pass
        d += _daydelta
    return sched.pop()
