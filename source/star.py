from datetime import datetime
from urllib.parse import quote_plus
from itertools import islice

from lxml.etree import fromstring, HTMLParser
from httplib2 import Http
from pytz import timezone

from schedule import Schedule
from util import nominative_month, add_year, fixyear, extract_text
from source.channels.starch import channel_code

source_tz = timezone('Europe/Kiev')
http = Http()
parser = HTMLParser()
hdrs = None


class SessionError(Exception):
    pass


def set_cookie(response):
    global hdrs
    hdrs = {'Cookie': response[0]['set-cookie']}


def do_get_schedule(content, tz):
    doc = fromstring(content, parser)

    prog = doc[1][2][1][2][0][3]
    if prog.tag != 'div':
        return []

    print_div = prog[4]
    if print_div.get('id') is None:
       return [] 
       
    schedule = Schedule(tz, source_tz)
    for row in islice(print_div[0], 0, None, 2):
        date_str = row[0][0].text
        if len(date_str) < 8:
            raise SessionError
        data = nominative_month(date_str)
        d = datetime.strptime(add_year(data), '%A, %d %B %Y')
        schedule.set_date(fixyear(d))
        for cell in row.getnext():
            for div in islice(cell, 0, None, 2):
                schedule.set_time(div.text)
                div = div.getnext()
                if len(div) == 0:
                    schedule.set_title(div.text)
                else:
                    info = div[0]
                    schedule.set_title(info.tail)
                    summary = ''.join(
                        map(extract_text, info.iter())
                    )
                    schedule.set_summary(summary)
    return schedule.pop()


def get_schedule(channel, tz):
    base_url = 'http://star.poltava.ua/index.php'
    if hdrs is None:
        set_cookie(http.request(base_url))

    channel = channel_code.get(channel) or channel
    url = (base_url + '?set_channel=' +
        quote_plus(channel, encoding='cp1251'))

    for i in range(2):
        try:
            response = http.request(url, headers=hdrs)
            return do_get_schedule(response[1], tz)
        except SessionError:
            set_cookie(response)
