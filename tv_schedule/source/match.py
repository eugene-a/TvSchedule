import datetime
import requests
import pytz
from tv_schedule import schedule


def need_channel_code():
    return False

_URL = 'http://matchtv.ru/ajax/week-schedule.xl'

_source_tz = pytz.UTC


def get_schedule(channel, tz):
    if channel != 'Матч ТВ':
        return []

    sched = schedule.Schedule(tz, _source_tz)

    for event in requests.get(_URL).json()['p']:
        dt = datetime.datetime.utcfromtimestamp(int(event['b']) * 60)
        sched.set_datetime(dt)
        sched.set_title(event['t'])
        sched.set_descr(event['s'])

    return sched.pop()
