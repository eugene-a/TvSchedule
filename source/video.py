from datetime import timedelta, datetime

from pytz import timezone
from httplib2 import Http
from lxml.etree import fromstring, HTMLParser

from schedule import Schedule
from source.channels.videoch import channel_code

source_tz = timezone('Europe/Moscow')

today = datetime.now(source_tz).date()
monday = today - timedelta(today.weekday())

del today

http = Http()
parser = HTMLParser()


def fetch(path):
    url = 'http://video.ru'
    content = http.request(url + path)[1]
    doc = fromstring(content, parser)
    return doc[1][0][0][4][1][0][0][0]   # innertube


def get_summary(path):
    p = fetch(path)[4]
    if p.tag == 'p':
        return p.text


def get_schedule(channel, tz):
    ch_code = channel_code.get(channel)
    if ch_code is  None:
        return []

    schedule = Schedule(tz, source_tz)
    d = monday
    summaries = {}

    for i in range(7):
        schedule.set_date(d)

        path = '/tv/index/' + ch_code + d.strftime('/%Y-%m-%d')

        table = fetch(path)[9][0]  # tvtopdata
        if table.tag != 'table':
            break

        for row in table.getnext():
            schedule.set_time(row[0].findtext('span'))

            cell3 = row[2]

            a = cell3.find('a')
            title = a.text
            schedule.set_title(title)

            summary = cell3.findtext('p') or summaries.get(title)
            if summary is None:
                summary = get_summary(a.get('href'))
                if summary:
                    summaries[title] = summary
            if summary:
                schedule.set_summary(summary)

        d += timedelta(1)

    return schedule.pop()
