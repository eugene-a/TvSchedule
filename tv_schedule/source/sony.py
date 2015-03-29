import datetime
import urllib.parse
import itertools
import pytz
import httplib2
import lxml.etree
from tv_schedule import schedule, dateutil


def need_channel_code():
    return False

_URL = None
_SCHED_URL = '/programma/ajax/{}/data/listings/%Y/%m/%d'

_channels = {
    'SET': ('http://www.set-russia.com', 'ru'),
    'Sony Sci-Fi': ('https://www.sonyscifi.ru', 'msk')
}

_source_tz = pytz.timezone('Europe/Moscow')
_daydelta = datetime.timedelta(1)
_http = httplib2.Http()
_parser = lxml.etree.HTMLParser(encoding='utf-8')


def _get_descr(url):
    url = urllib.parse.urljoin(_URL, url)
    content = _http.request(url)[1]
    doc = lxml.etree.fromstring(content, _parser)
    sb_site = next(itertools.islice(doc[2].iterchildren('div'), 1, 2))
    cont = sb_site[0][2][0][0][0][0][0][2][0][0][1]
    return '\n'.join(x.text or '' for x in cont)


class _Descriptions:
    def __init__(self):
        self._cash = {}

    def get(self, a):
        href = a.get('href')
        key = href[href.index('/') + 1:]
        descr = self._cash.get(key)
        if descr is None:
            self._cash[key] = descr = _get_descr(href)
        return descr


def get_schedule(channel, tz):
    global _URL
    _URL, ru = _channels.get(channel) or (None, None)
    if _URL is None:
        return []

    prog_url = _SCHED_URL.format(ru)

    today = dateutil.tv_date_now(_source_tz)
    weekday_now = today.weekday()
    sched = schedule.Schedule(tz, _source_tz)

    descriptions = _Descriptions()

    d = today
    for i in range(weekday_now, 7):
        sched.set_date(d)

        url = urllib.parse.urljoin(_URL, d.strftime(prog_url))
        content = _http.request(url)[1]
        doc = lxml.etree.fromstring(content, _parser)
        for li in (x for x in doc[0][0] if len(x) > 0):
            sched.set_time(li[0][1].text)
            cont = li[2]
            title = cont[0]
            if len(title) == 0:
                sched.set_title(title.text)
            else:
                a = title[0]
                sched.set_title(a.text)
                descr = (cont[1].text + '\n' + cont[2].text + '\n' +
                         descriptions.get(a))
                sched.set_descr(descr)
        d += _daydelta
    return sched.pop()
