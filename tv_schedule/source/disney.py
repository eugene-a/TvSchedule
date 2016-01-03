import datetime
import pytz
import requests
import lxml.html
from tv_schedule import schedule, dateutil


def need_channel_code():
    return False

_URL = 'http://www.disney.ru/kanal/program/export/tv-schedule?'
_source_tz = pytz.timezone('Europe/Moscow')
_daydelta = datetime.timedelta(1)


def get_schedule(channel, tz):
    if channel != 'Disney Channel':
        return []

    today = dateutil.tv_date_now(_source_tz)
    weekday_now = today.weekday()
    sched = schedule.Schedule(tz, _source_tz)

    d = today
    for i in range(weekday_now, 7):
        sched.set_date(d)
        param = {'date': d.strftime('%d-%m-%Y')}
        sch = requests.get(_URL, param).json()
        programs = sch['programs']
        for event in sch['seances']:
            sched.set_time(event['time'])
            try:
                program = programs[str(event['programId'])]
            except KeyError:
                sched.set_title(event['title'])
            else:
                sched.set_title(program['title'])
                descr = lxml.html.fromstring(program['description'])
                sched.set_descr(descr.text_content())
        d += _daydelta
    return sched.pop()
