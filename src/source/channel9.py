from datetime import datetime, timedelta
from itertools import islice
from lxml.etree import parse, HTMLParser
from pytz import timezone
from schedule import Schedule


def fetch():
    url = 'http://9tv.co.il/tv-shows/'
    etree = parse(url, HTMLParser())
    return  etree.getroot()[1][1][6][0]


def get_schedule(channel, tz):
    source_tz = timezone('Israel')
    today = datetime.now(source_tz).date()
    weekday = today.weekday()
    sunday = today if weekday == 6 else today - timedelta(weekday + 1)
    daydelta = timedelta(1)

    schedule = Schedule(tz, source_tz)

    d = sunday
    for tv_program in islice(fetch(), 2, 9):
        schedule.set_date(d)
        for li in tv_program[0]:
            span = li[0]
            schedule.set_time(span.text)
            schedule.set_title(span.tail)
        d += daydelta

    return schedule.pop()
