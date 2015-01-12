from datetime import datetime, timedelta

from lxml.etree import HTMLParser, parse
from pytz import timezone

from schedule import Schedule


class Target:
    def __init__(self, schedule):
        self.schedule = schedule

    def start(self, tag, attrib):
        self.elem_class = attrib.get('class')
        self.data_str = ''

    def data(self, data):
        self.data_str += data

    def end(self, tag):
        if self.elem_class == 'value time':
            self.schedule.set_time(self.data_str)
        elif self.elem_class == 'summary':
            title = self.data_str.replace(':', ';')
            self.schedule.set_title(title)
        elif self.elem_class == 'synopsis':
            self.schedule.set_summary(self.data_str)
        self.elem_class = None

    def close(self):
        pass


def get_schedule(channel, tz):
    schedule = Schedule(tz, timezone('Europe/Berlin'))
    parser = HTMLParser(target=Target(schedule))

    url = 'http://www.bbcentertainment.com/europe/schedule/?date='

    d = datetime.now(tz).date()
    for i in range(7):
        schedule.set_date(d)
        query = d.strftime('%Y-%m-%d')
        print(query)
        parse(url + query, parser)
        d += timedelta(1)

    return schedule.pop()
