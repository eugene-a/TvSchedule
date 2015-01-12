from datetime import date, timedelta

from lxml.etree import HTMLParser, parse
from pytz import timezone

from schedule import Schedule


class Target:
    def __init__(self, schedule):
        self.schedule = schedule
        today = date.today()
        self.date = today - timedelta(today.weekday())
        self.span_id = None

    def start(self, tag, attrib):
        self.data_str = ''
        if tag == 'table':
            self.schedule.set_date(self.date)
            self.date += timedelta(1)
        elif tag == 'span':
            self.span_id = attrib.get('id')

    def data(self, data):
        self.data_str += data

    def end(self, tag):
        if tag == 'span':
            id = self.span_id
            if id is not None:
                schedule = self.schedule
                if id.endswith('_RunTime'):
                    schedule.set_time(self.data_str)
                elif id.endswith('_ProgramName'):
                    schedule.set_title(self.data_str)

    def close(self):
        pass


def get_schedule(channel, tz):
    schedule = Schedule(tz, timezone('Europe/Riga'))

    url = 'http://service.rumusic.tv/service/schedule.aspx'
    parse(url, HTMLParser(encoding='utf-8', target=Target(schedule)))

    return schedule.pop()
