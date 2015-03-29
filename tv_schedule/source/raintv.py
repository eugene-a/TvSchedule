import datetime
import pytz
import httplib2
import lxml.html
from tv_schedule import schedule, dateutil


def need_channel_code():
    return False

_URL = 'http://tvrain.ru/schedule/%Y-%m-%d/'
_source_tz = pytz.timezone('Europe/Moscow')
_daydelta = datetime.timedelta(1)

_http = httplib2.Http()


def get_schedule(channel, tz):
    if channel != 'Дождь':
        return []

    today = dateutil.tv_date_now(_source_tz)
    weekday_now = today.weekday()
    sched = schedule.Schedule(tz, _source_tz)

    d = today
    for i in range(weekday_now, 7):
        content = _http.request(d.strftime(_URL))[1]
        doc = lxml.html.fromstring(content)
        stacked = doc[1][8][3][0][0][0][3]
        for part in stacked[1::2]:
            for article in part.iterchildren('article'):
                dt_str = article[-3][0].get('datetime')
                dt = datetime.datetime.strptime(dt_str, '%Y-%m-%d %H:%M:%S')
                sched.set_datetime(dt)
                sched.set_title(article[-2][0][0].text)
                sched.set_descr(article[-1].text_content())
        d += _daydelta
    return sched.pop()
