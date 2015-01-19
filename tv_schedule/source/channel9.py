from datetime import datetime, timedelta
from itertools import islice
from lxml.etree import parse, HTMLParser
from pytz import timezone

from dateutil import last_weekday
from schedule import Schedule

LOAD_CHANNEL_CODE = False


def fetch(url, parser):
    etree = parse(url, parser)
    return etree.getroot()[1][1][6][0]


def get_schedule(channel, tz):
    source_tz = timezone('Israel')
    daydelta = timedelta(1)

    schedule = Schedule(tz, source_tz)

    url = 'http://9tv.co.il/tv-shows/'
    parser = HTMLParser()

    d = last_weekday(datetime.now(source_tz).date(), 6)  # start from Sunday

    for tv_program in islice(fetch(url, parser), 2, 9):
        schedule.set_date(d)
        for li in tv_program[0]:
            span = li[0]
            schedule.set_time(span.text)
            schedule.set_title(span.tail)
        d += daydelta

    return schedule.pop()
