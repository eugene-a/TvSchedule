import datetime
import urllib.parse
import itertools
import httplib2
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

_http = httplib2.Http()


def _fetch(url):
    url = urllib.parse.urljoin(_URL, url)
    content = _http.request(url)[1]
    doc = lxml.html.fromstring(content, parser=_parser)
    main = doc.get_element_by_id('main')
    return main[0]


def _get_descr(url):
    try:
        cont = _fetch(url)
        if cont.get('id') == 'blocks':
            b = next(
                (x for x in cont if x.get('data-block_id') == 'about_full')
            )
            return b[1][0].text_content().replace('\t', '')
    except StopIteration:
        pass


class _Descriptions:
    def __init__(self):
        self._cash = {}

    def get(self, a):
        url = a.get('href')
        path = urllib.parse.urlsplit(url).path
        if path != '/':
            key = int(path.split('/')[-1])
            descr = self._cash.get(key)
            if descr is None:
                self._cash[key] = descr = _get_descr(url)
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
