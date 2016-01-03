import datetime
import pytz
import requests
import lxml.html
from tv_schedule import schedule, dateutil


def need_channel_code():
    return False

_URL = 'http://tvrain.ru/schedule/%Y-%m-%d/'
_source_tz = pytz.timezone('Europe/Moscow')
_daydelta = datetime.timedelta(1)


def get_schedule(channel, tz):
    if channel != 'Дождь':
        return []

    today = dateutil.tv_date_now(_source_tz)
    weekday_now = today.weekday()
    sched = schedule.Schedule(tz, _source_tz)

    d = today
    for i in range(weekday_now, 7):
        resp = requests.get(d.strftime(_URL))
        doc = lxml.html.fromstring(resp.content)
        layout = next(x for x in doc[1] if x.get('class') == 'layout')
        for part in layout[6][0][0][0][3][1::2]:
            for article in part.iterchildren('article'):
                dt_str = article[-3][0].get('datetime')
                dt = datetime.datetime.strptime(dt_str, '%Y-%m-%d %H:%M:%S')
                sched.set_datetime(dt)
                sched.set_title(article[-2][0][0].text)
                sched.set_descr(article[-1].text_content())
        d += _daydelta
    return sched.pop()
