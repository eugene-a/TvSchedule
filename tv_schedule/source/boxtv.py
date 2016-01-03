import datetime
import pytz
import requests
import lxml.etree
from tv_schedule import schedule, dateutil


def need_channel_code():
    return False


_URL = 'http://boxingtv.ru/schedule/%Y/%m/%d'
_source_tz = pytz.timezone('Europe/Moscow')
_parser = lxml.etree.HTMLParser()
_daydelta = datetime.timedelta(1)


def get_schedule(channel, tz):
    if channel != 'Бокс ТВ':
        return []

    today = dateutil.tv_date_now(_source_tz, 0)
    weekday_now = today.weekday()
    sched = schedule.Schedule(tz, _source_tz)

    d = today
    for i in range(weekday_now, 7):
        sched.set_date(d)
        url = d.strftime(_URL)
        resp = requests.get(url)
        doc = lxml.etree.fromstring(resp.content, _parser)
        rasp = doc[1][1][2][0][4]
        for event in rasp:
            it = event.iterchildren()
            time = next(it)[0].text
            sched.set_time(time)
            it = next(it)[0].iterchildren()
            title = next(it).text
            sched.set_title(title)
            descr = next(it).text
            sched.set_descr(descr)
        d += _daydelta
    return sched.pop()
