import datetime
import json
import urllib.parse
import pytz
import httplib2
import lxml.html
from tv_schedule import schedule, dateutil


def need_channel_code():
    return False

_URL = 'http://www.disney.ru/kanal/program/export/tv-schedule?'
_source_tz = pytz.timezone('Europe/Moscow')
_daydelta = datetime.timedelta(1)
_http = httplib2.Http()


def get_schedule(channel, tz):
    if channel != 'Disney Channel':
        return []

    today = dateutil.tv_date_now(_source_tz)
    weekday_now = today.weekday()
    sched = schedule.Schedule(tz, _source_tz)

    d = today
    for i in range(weekday_now, 7):
        sched.set_date(d)
        query = {'date': d.strftime('%d-%m-%Y')}
        url = _URL + urllib.parse.urlencode(query)
        content = _http.request(url)[1]
        sch = json.loads(content.decode())
        programs = sch['programs']
        for event in sch['seances']:
            sched.set_time(event['time'])
            program = programs[str(event['programId'])]
            sched.set_title(program['title'])
            descr = lxml.html.fromstring(program['description'])
            sched.set_descr(descr.text_content())
        d += _daydelta
    return sched.pop()
