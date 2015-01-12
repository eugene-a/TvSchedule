from datetime import datetime

from lxml.etree import HTMLParser, fromstring
from httplib2 import Http
from pytz import timezone

from schedule import Schedule
from util import nominative_month, fixyear


class Target:
    def __init__(self, schedule):
        self.schedule = schedule

    def start(self, tag, attrib):
        self.elem_class = attrib.get('class')
        self.data_str = ''

    def data(self, data):
        self.data_str += data

    def end(self, tag):
        if self.elem_class == 'tvguide_day':
            date = self.data_str
            date = date[date.find(','):]
            date = datetime.strptime(nominative_month(date), ', %d %B')
            self.schedule.set_date(fixyear(date))
        elif self.elem_class == 'tvguide_time':
            self.schedule.set_time(self.data_str)
        elif self.elem_class == 'tvguide_title':
            self.schedule.set_title(self.data_str)

        self.elem_class = None

    def close(self):
        pass


def get_schedule(channel, tz):
    schedule = Schedule(tz, timezone('Europe/Berlin'))
    parser = HTMLParser(target=Target(schedule))

    http = Http()
    base_url = 'http://www.tcmeurope.com/ru/tvguide.php?days_ahead='

    for days_ahead in '0', '3', '6':
        url = base_url + days_ahead
        fromstring(http.request(url)[1], parser)

    return schedule.pop()
