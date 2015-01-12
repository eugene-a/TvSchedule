from datetime import timedelta, datetime

from pytz import timezone
from httplib2 import Http
from lxml.etree import fromstring, HTMLParser

from schedule import Schedule
from source.channels.obzorch import channel_code

BASE_URL =  'http://www.obzor.lt/tv/'

source_tz = timezone('Europe/Vilnius')

today = datetime.now(source_tz).date()
monday = today - timedelta(today.weekday())

del today

daydelta = timedelta(1)

http = Http()
parser = HTMLParser()


def get_schedule(channel, tz):
    ch_code = channel_code.get(channel)
    if ch_code is  None:
        return []
        
 
    schedule = Schedule(tz, source_tz)
    d = monday
    
    ch_url = BASE_URL + ch_code
    
    for i in range(7):
        schedule.set_date(d)
        content = http.request( ch_url +d.strftime('/%Y-%m-%d'))[1]
        doc = fromstring(content, parser)
        program_list = doc[1][0][7][0][0][0][1]
        if program_list.get('class') == 'tv_program_list':
            for row in program_list[0][0][0][0][0][0][0]:
                schedule.set_time(row[0].text)
                schedule.set_title(row[1].text)

        d += daydelta

    return schedule.pop()
