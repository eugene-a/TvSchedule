from datetime import datetime
from itertools import islice

from lxml.etree import fromstring, HTMLParser
from httplib2 import Http
from pytz import timezone

from schedule import Schedule
from util import nominative_month, add_year, fixyear
from source.channels.vsetvch import channel_code


source_tz = timezone('Europe/Kiev')

USER_AGENT = \
    'Mozilla/5.0 (Windows NT 6.2; WOW64; rv:22.0) Gecko/20100101 Firefox/22.0'
HEADERS = {'user-agent': USER_AGENT}
del USER_AGENT

http = Http()
parser = HTMLParser()


def fetch(path):
    url = 'http://www.vsetv.com/'
    content = http.request(url + path, headers=HEADERS)[1]
    doc = fromstring(content, parser)
    return doc[3][6][3][0]  # main    (4 comments between top and base tables)


def get_summary(path):
    table = fetch(path)[1]
    if table.get('id') is None:
        return

    summary = ''

    row = table[0]

    elem = row[0][0]
    if elem.tail is not None:
        summary += elem.tail + '\n'

    elem = elem.getnext().getnext()
    if elem.tail is None:
        elem = elem.getnext()
    summary += elem.tail.lstrip()

    elem = elem.getnext()
    if elem.tag == 'strong':
        summary += elem.text

    summary += '\n'

    row = row.getnext()
    for elem in row[0]:
        if elem.tag == 'br':
            summary += '\n'
        elif elem.tag == 'div':
            summary += elem.findtext('span')
            break
        else:
            summary += elem.text + elem.tail

    return  summary


def get_schedule(channel, tz):
    ch_code = channel_code.get(channel)
    if ch_code is None:
        return []

    path = 'schedule_channel_' + ch_code + '_week.html'

    schedule = Schedule(tz, source_tz)
    summaries = {}

    for div in islice(fetch(path), 6, None):
        if div.get('class') == 'sometitle':
            data = div[0][0][0].text
            data = nominative_month(data)
            d = datetime.strptime(add_year(data), '%A, %d %B %Y')
            schedule.set_date(fixyear(d))
        else:
            for subd in div:
                subd_class = subd.get('class')
                if subd_class == 'time':
                    schedule.set_time(subd.text)
                elif subd_class == 'prname2':
                    a = subd.find('a')
                    if a is None:
                        title = (
                            subd.text if len(subd) == 0 else subd[0].tail[1:]
                        )
                        schedule.set_title(title)
                    else:
                        schedule.set_title(a.text)
                        path = a.get('href')
                        key = path[: path.find('.')]
                        summary = summaries.get(key)
                        if summary is None:
                            summary = get_summary(path)
                            summaries[key] = summary
                        if summary:
                            schedule.set_summary(summary)
    return schedule.pop()
