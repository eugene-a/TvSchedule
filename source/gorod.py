from datetime import  datetime, timedelta
from httplib2 import Http
from lxml.etree import HTMLParser, fromstring
from pytz import timezone
from schedule import Schedule
from source.channels.gorodch import channel_code


source_tz = timezone('Europe/Riga')
http = Http()
parser = HTMLParser(encoding='utf-8')

today = datetime.now(source_tz).date()
monday = today - timedelta(today.weekday())
del today

daydelta = timedelta(1)

def get_schedule(channel, tz):
    ch_code = channel_code.get(channel)
    if ch_code is  None:
        return []
        
    url_base = 'http://www.gorod.lv/tv/' + ch_code + '/'
    schedule = Schedule(tz, source_tz)

    d = monday
    for i in range(7):
        schedule.set_date(d)
        url = url_base + d.strftime('%d.%m.%Y')
        doc = fromstring(http.request(url)[1], parser)
        ul = doc[1][2][0][7][0][0][0][5]
        if ul.tag == 'ul':
            for li in ul:
                span = li[0]
                schedule.set_time(span.text)
                schedule.set_title(span.tail.strip())
            d += daydelta
    return schedule.pop()
