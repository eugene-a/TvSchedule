from datetime import datetime, timedelta

from lxml.etree import HTMLParser, fromstring
from httplib2 import Http
from pytz import timezone

from schedule import Schedule


class State:
    time, title = 0, 1


class Target:
    def __init__(self, schedule):
        self.schedule = schedule
        self.state = None
        self.data_str = ''

    def start(self, tag, attrib):
        if attrib.get('class') == 'time':
            self.state = State.time

    def data(self, data):
        if self.state is not None:
            self.data_str += data

    def end(self, tag):
        if self.state == State.time:
            self.schedule.set_time(self.data_str)
            self.state = State.title
        elif self.state == State.title:
            self.schedule.set_title(self.data_str)
            self.state = None
        self.data_str = ''

    def close(self):
        pass


def get_schedule(channel, tz):
    schedule = Schedule(tz, timezone('Europe/Riga'))
    parser = HTMLParser(target=Target(schedule))

    http = Http()
    base_url = 'http://www.1tv.lv/programma.php?date='

    d = datetime.now(tz).date()
    for i in range(d.weekday(), 7):
        schedule.set_date(d)
        url = base_url + d.strftime('%Y-%m-%d')
        fromstring(http.request(url)[1], parser)
        d += timedelta(1)

    return schedule.pop()
