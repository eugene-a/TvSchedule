import datetime
import urllib.parse
import pytz
import requests
import lxml.etree
from tv_schedule import schedule, dateutil


def need_channel_code():
    return False

_URL = 'http://www.tv-stream.ru'
_SCHED_URL = '/schedule.ajax'
_EVENT_URL = '/telecast.ajax'

_sched_url = urllib.parse.urljoin(_URL, _SCHED_URL) + '?'
_event_url = urllib.parse.urljoin(_URL, _EVENT_URL) + '?'

_source_tz = pytz.timezone('Europe/Moscow')
_daydelta = datetime.timedelta(1)
_parser = lxml.etree.HTMLParser()

_channels = {
    'Охота и рыбалка': '6',
    'Ретро': '8',
    'Драйв': '4',
    'Вопросы и ответы': '2',
    'Усадьба': '9',
    'Здоровое Телевидение': '5',
    'ПСИХОЛОГИЯ21': '7'
}


def _fetch(url, params):
    return requests.get(url, params).json()


def _get_descr(id):
    return _fetch(_event_url, {'program_id': id})['annotation']


class _Descriptions:
    def __init__(self):
        self._cash = {}

    def get(self, a):
        key = int(a.get('data-program_id'))
        descr = self._cash.get(key)
        if descr is None:
            self._cash[key] = descr = _get_descr(key)
        return descr


def get_schedule(channel, tz):
    chan = _channels.get(channel)
    if chan is None:
        return []

    descriptions = _Descriptions()

    params = {'channel': chan, 'type': 'week'}
    today = dateutil.tv_date_now(_source_tz)

    weekday_now = today.weekday()
    sched = schedule.Schedule(tz, _source_tz)

    d = today
    for i in range(weekday_now, 7):
        sched.set_date(d)
        params['year'], params['week'], params['dayOfWeek'] = d.isocalendar()
        list = _fetch(_sched_url, params)['list']
        doc = lxml.etree.fromstring(list, _parser)
        for li in doc[0][0][0]:
            sched.set_time(li[0].text)
            a = li[1]
            sched.set_title(a.text)
            sched.set_descr(descriptions.get(a))
        d += _daydelta
    return sched.pop()
