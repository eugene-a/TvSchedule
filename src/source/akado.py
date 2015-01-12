from datetime import timedelta, datetime

from pytz import timezone
from httplib2 import Http
from lxml.etree import fromstring, HTMLParser

from schedule import Schedule
from source.channels.akadoch import channel_code

source_tz = timezone('Europe/Moscow')

today = datetime.now(source_tz).date()
monday = today - timedelta(today.weekday())

del today

daydelta = timedelta(1)

http = Http()
parser = HTMLParser(encoding='utf-8')


def fetch(path):
    url = 'http://tv.akado.ru/channels/'
    content = http.request(url + path)[1]
    tv_layout = fromstring(content, parser)[1][0][4]
    if tv_layout.get('class') is not None:
        return tv_layout[0][0]   # tv-common


def get_schedule(channel, tz):
    ch_code = channel_code.get(channel)
    if ch_code is None:
        return []

    schedule = Schedule(tz, source_tz)
    d = monday

    for i in range(7):
        schedule.set_date(d)
        path = ch_code + d.strftime('.html?date=%Y-%m-%d')
        tv_common = fetch(path)
        if tv_common is None:
            break

        program = tv_common[1]

        for row in program.find('table'):    # tv-channel-full
            schedule.set_time(row[0][0].text)
            cell = row[1]
            schedule.set_title(cell[0].text)
            summary = cell[1].text
            if summary is not None:
                schedule.set_summary(summary)

        d += daydelta

    return schedule.pop()
