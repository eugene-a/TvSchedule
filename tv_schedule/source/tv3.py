import datetime
import urllib.parse
import pytz
import requests
from tv_schedule import schedule, dateutil


def need_channel_code():
    return False

_source_tz = pytz.timezone('Europe/Moscow')
_URL = 'http://tv3.ru/wp-admin/admin-ajax.php'

_fields = {
    'description': '',
    'genre': '',
    'production': '',
    'stage_manager': 'Режиссёр: ',
    'actors': 'В ролях: '
}


def get_schedule(channel, tz):
    if channel != 'ТВ3':
        return []

    sched = schedule.Schedule(tz, _source_tz)

    today = dateutil.tv_date_now(_source_tz)
    data = {
        'action': 'get_shedule_list',
        'dey': today.strftime('%Y-%m-%d')
    }

    resp = requests.post(_URL, data)
    days = resp.json()
    for day in days:
        for ev in days[day]:
            dt_str = ev['broadcast_time']
            dt = datetime.datetime.strptime(dt_str, '%Y-%m-%d %H:%M:%S')
            sched.set_datetime(dt)
            sched.set_title(ev['long_name'])

            descr = ''
            for name in _fields:
                field = ev[name]
                if field:
                    descr += _fields[name] + field + '\n'
                if descr:
                    sched.set_descr(descr)
    return sched.pop()
