from datetime import timedelta, datetime

from pytz import timezone
from httplib2 import Http
from lxml.etree import fromstring, HTMLParser
from schedule import Schedule


BASE_URL =  'http://www.1tv.lv/programma.php?date='

source_tz = timezone('Europe/Riga')

today = datetime.now(source_tz).date()
monday = today - timedelta(today.weekday())

del today

daydelta = timedelta(1)

http = Http()
parser = HTMLParser()


def get_schedule(channel, tz):
    schedule = Schedule(tz, source_tz)
    d = monday
    
    for i in range(7):
        schedule.set_date(d)
        content = http.request( BASE_URL +d.strftime('%Y-%m-%d'))[1]
        doc = fromstring(content, parser)
     
        for li in doc[1][0][0][0][4][0][0][0][0][4]:
            span = li[0]
            schedule.set_time(span.text)
            schedule.set_title(span.tail)

        d += daydelta

    return schedule.pop()
