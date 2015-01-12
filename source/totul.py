from itertools import islice
from datetime import  datetime, timedelta
from httplib2 import Http
from lxml.etree import HTMLParser, fromstring
from pytz import timezone
from schedule import Schedule
from source.channels.totulch import channel_code


source_tz = timezone('Europe/Chisinau')
http = Http()
parser = HTMLParser()

today = datetime.now(source_tz).date()
monday = today - timedelta(today.weekday())
del today

daydelta = timedelta(1)

def get_schedule(channel, tz):
    ch_code = channel_code.get(channel)
    if ch_code is None:
        return []

    pattern = 'http://totul.md/en/tv.html?when=allday&date=%Y-%m-%d&channel='

    schedule = Schedule(tz, source_tz)

    d = monday
    for i in range(7):
        schedule.set_date(d)
        url = d.strftime(pattern) + ch_code
        doc = fromstring(http.request(url)[1], parser)
        tvilist = doc[1][12][0][0][0][7]
        if len(tvilist) > 0:
            start = 3 if tvilist[0].tag == "h2" else 4
            for div in islice(tvilist,  start,  None,  3):
                schedule.set_time(div.text)
                schedule.set_title(div.getnext().text)
            d += daydelta
    return schedule.pop()

