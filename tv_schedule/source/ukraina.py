import datetime
import pytz
import requests
import lxml.html
from tv_schedule import schedule, dateutil


def need_channel_code():
    return False

_URL = 'http://kanalukraina.tv/ru/schedule/single/schedule/%d-%m-%Y/'
_source_tz = pytz.timezone('Europe/Kiev')
_daydelta = datetime.timedelta(1)
_parser = lxml.html.HTMLParser(encoding='utf-8')


def _fetch(url):
    resp = requests.get(url)
    doc = lxml.html.fromstring(resp.content, parser=_parser)
    return doc[1]


def _get_descr(url):
    body = _fetch(url)
    if body.get('class') != 'ru':
        return ''
    else:
        text = body[5][0][1][0][0][1][1][-1][0][-1]
        for br in text.iterdescendants('br'):
            br.tail = '\n' + (br.tail or '')
        return text.text_content()


class _Descriptions:
    def __init__(self):
        self._cash = {}

    def get(self, a):
        href = a.get('href')
        if href:
            key = int(href[href.rindex('/', 0, -1) + 1: -1])
            descr = self._cash.get(key)
            if descr is None:
                self._cash[key] = descr = _get_descr(href)
            return descr


def get_schedule(channel, tz):
    if channel != 'Украина':
        return []

    today = dateutil.tv_date_now(_source_tz)
    weekday_now = today.weekday()
    sched = schedule.Schedule(tz, _source_tz)
    descriptions = _Descriptions()
    d = today
    for i in range(weekday_now, 7):
        sched.set_date(d)
        for li in _fetch(d.strftime(_URL))[0][1]:
            info = li[2]
            it = info.iterchildren()
            time = next(it).text
            sched.set_time(time)
            name = next(it)
            if len(name) == 0:
                sched.set_title(name.text)
            else:
                a = name[0]
                sched.set_title(a.text)
                zoo = info.getnext()[0][1]
                descr = descriptions.get(a)
                if not descr:
                    zoo = info.getnext()[0][1]
                    if len(zoo) > 0:
                        descr = zoo[0].text
                sched.set_descr(descr)
        d += _daydelta
    return sched.pop()
