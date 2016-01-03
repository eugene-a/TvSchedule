import datetime
import urllib.parse
import pytz
import requests
import lxml.html
from tv_schedule import schedule, dateutil


def need_channel_code():
    return False


_URL = 'http://www.{}.tv'
_SCHED_URL = '/guides'
_url = None

_channels = {
    'Телепутешествия': 'teletravel',
    'Охотник и рыболов': 'ohotnikirybolov'
}
_source_tz = pytz.timezone('Europe/Moscow')
_daydelta = datetime.timedelta(1)


def _fetch(url, params=None):
    url = urllib.parse.urljoin(_url, url)
    resp = requests.get(url, params)
    doc = lxml.html.fromstring(resp.content)
    return doc[1][4][0][0][0][2]


def _get_descr(url):
    zoo = _fetch(url)
    return zoo[0].text_content()


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
    chan = _channels.get(channel)
    if chan is None:
        return []

    global _url;
    _url = _URL.format(chan)

    today = dateutil.tv_date_now(_source_tz, 0)
    weekday_now = today.weekday()
    sched = schedule.Schedule(tz, _source_tz)

    descriptions = _Descriptions()

    d = today
    for i in range(weekday_now, 7):
        sched.set_date(d)
        param = {'date': d.strftime('%Y-%m-%d')}
        for event in _fetch(_SCHED_URL, param)[1:]:
            it = event.iterchildren()
            next(it)
            sched.set_time(next(it)[0].text)
            title = next(it)
            if len(title) == 0:
                sched.set_title(title.text.strip())
            else:
                a = title[0]
                if a.tag != 'a':  # now
                    sched.set_title(title[1][0].text_content())
                else:
                    sched.set_title(a.text)
                    sched.set_descr(descriptions.get(a))
        d += _daydelta
    return sched.pop()
