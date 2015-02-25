import time
import urllib.parse
import datetime
import json
import httplib2
import lxml.html
from tv_schedule import schedule, dateutil


def need_channel_code():
    return True

channel_code = None

_URL = 'http://tv.mail.ru/ext/admtv/?'

_chan_query = {'sch.main': 1}

_daydelta = datetime.timedelta(1)

_http = httplib2.Http()

# Avoid 'robot' detection
_THROTTLE = 2
_BURST = 10

_counter = _BURST
_last_clock = -_THROTTLE


def _throttle():
    global _counter, _last_clock

    _counter -= 1
    next_clock = time.clock()

    if _counter > 0:
        tosleep = 0
    else:
        _counter = _BURST
        tosleep = _THROTTLE - (next_clock - _last_clock)

    if tosleep > 0:
        time.sleep(tosleep)
        _last_clock += _THROTTLE
    else:
        _last_clock = next_clock


def _fetch(url):
    _throttle()
    return json.loads(_http.request(url)[1].decode())


def _get_descr(event):
    query = urllib.parse.urlencode({'sch.tv_event_id': event['id']})
    url = _URL + query
    event = _fetch(url)['tv_event']
    html = lxml.html.fragment_fromstring(event['descr'], create_parent=True)
    return html.text_content()


class _EventInfo:
    def __init__(self):
        self._cash = {}

    def get(self, event):
        title = event['name']
        descr = self._cash.get(title)
        if descr is None:
            self._cash[title] = descr = _get_descr(event)
        return title, descr


def get_schedule(channel, tz):
    ch_code = channel_code.get(channel)
    if ch_code is None:
        return []

    today = dateutil.tv_date_now(tz)
    weekday_now = today.weekday()

    sched = schedule.Schedule(tz, tz)
    event_info = _EventInfo()
    _chan_query['sch:channel'] = ch_code
    d = today
    for i in range(weekday_now, 7):
        _chan_query['sch.date'] = d.strftime('%Y-%m-%d')
        url = _URL + urllib.parse.urlencode(_chan_query)
        chan_type = _fetch(url)['channel_type']
        sch = next(iter((chan_type.values())))[0]['schedule']
        for event in sch:
            fmt = '%Y-%m-%d %H:%M:%S'
            dt = datetime.datetime.strptime(event['start'], fmt)
            sched.set_datetime(dt)
            title, descr = event_info.get(event)
            sched.set_title(title)
            sched.set_descr(descr)
        d += _daydelta
    return sched.pop()
