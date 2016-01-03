import datetime
import pytz
import requests
import lxml.html
from tv_schedule import schedule, dateutil


def need_channel_code():
    return True

channel_code = None

_URL = 'http://www.tv.lv/kanali/'
_source_tz = pytz.timezone('Europe/Riga')
_daydelta = datetime.timedelta(1)


def get_schedule(channel, tz):
    ch_code = channel_code.get(channel)
    if ch_code is None:
        return []

    url = _URL + ch_code + '/'
    today = dateutil.tv_date_now(_source_tz, 0)
    weekday_now = today.weekday()
    sched = schedule.Schedule(tz, _source_tz)

    d = today
    for i in range(0, 7 - weekday_now):
        sched.set_date(d)
        resp = requests.get(url + str(i) + '/')
        doc = lxml.html.fromstring(resp.content)
        page_channel = doc[1][7][2][0][0][2][0][0][0][0][1][0]
        row = page_channel[0][0][0][1][0][0][2]
        if len(row) > 0:
            for event in (x for x in row[0] if x.get('id') == 'programrow'):
                it = event.iterchildren()
                sched.set_time(next(it).text)
                div = next(it)
                title = next(div.iterchildren('a')).text_content()
                sched.set_title(title.split(' (')[0])
                sched.set_descr(div[0].get('value').split(';;')[1])
        d += _daydelta
    return sched.pop()
