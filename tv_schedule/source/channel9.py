import datetime
import itertools
import lxml.etree
import pytz

from tv_schedule import dateutil, schedule


def need_channel_code():
    return False


def _fetch(url, parser):
    etree = lxml.etree.parse(url, parser)
    return etree.getroot()[1][1][6][0]


def get_schedule(channel, tz):
    source_tz = pytz.timezone('Israel')
    daydelta = datetime.timedelta(1)

    sched = schedule.Schedule(tz, source_tz)

    url = 'http://9tv.co.il/tv-shows/'
    parser = lxml.etree.HTMLParser()

    # start from Sunday
    d = dateutil.last_weekday(datetime.datetime.now(source_tz).date(), 6)

    for tv_program in itertools.islice(_fetch(url, parser), 2, 9):
        sched.set_date(d)
        for li in tv_program[0]:
            span = li[0]
            sched.set_time(span.text)
            sched.set_title(span.tail)
        d += daydelta

    return sched.pop()
