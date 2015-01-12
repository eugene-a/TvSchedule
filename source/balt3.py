from datetime import datetime, timedelta
from string import punctuation

from lxml.etree import HTMLParser, fromstring
from httplib2 import Http
from pytz import timezone

from schedule import Schedule


class Target:
    def __init__(self, schedule):
        self.schedule = schedule
        self.inside_prog = False

    def start(self, tag, attrib):
        if tag == 'span' and attrib.get('class') == 'text':
            self.inside_prog = True
            self.data_str = ''

    def data(self, data):
        if self.inside_prog:
            self.data_str += data.strip()

    def end(self, tag):
        if self.inside_prog:
            if tag == 'br':
                time, title = self.data_str.split(None, 1)
                self.data_str = ''
                title = title.split('\r\n\t')
                if title[0][-1] not in punctuation:
                    title[0] += '.'
                self.schedule.set_time(time)
                self.schedule.set_title(' '.join(title))
            elif tag == 'span':
                self.inside_prog = False

    def close(self):
        pass


def get_schedule(channel, tz):
    schedule = Schedule(tz, timezone('Europe/Riga'))
    parser = HTMLParser(target=Target(schedule))

    http = Http()
    url_pattern = 'http://www.3plus.lv/content/blogcategory/71{0}/'

    d = datetime.now(tz).date()
    i = wd = d.weekday() % 7 + 3

    while True:
        schedule.set_date(d)
        url = url_pattern.format(i)
        fromstring(http.request(url)[1], parser)
        i = i + 1 if i < 9 else 3
        if i == wd:
            break
        d += timedelta(1)

    return schedule.pop()
