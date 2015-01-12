from datetime import datetime, timedelta

from httplib2 import Http
from pytz import timezone
from lxml.etree import HTMLParser, fromstring

from schedule import Schedule
from source.channels.gorodch import channel_code


class State:
    init, time, title = range(3)


class Target:
    def __init__(self):
        self.state = State.init
        self.data_str = ''

    def start(self, tag, attrib):
        if tag == 'span' and self.state == State.init:
            if attrib.get('class') == 'time':
                self.state = State.time

    def data(self, data):
        if self.state > 0:
            self.data_str += data

    def end(self, tag):
        if self.state == State.time:
            self.schedule.set_time(self.data_str)
            self.state = State.title
        elif self.state == State.title:
                self.schedule.set_title(self.data_str)
                self.state = State.init
        self.data_str = ''

    def close(self):
        pass


class Fetcher:
    def __init__(self):
        self.http = Http()
        self.tz = timezone('Europe/Riga')
        today = datetime.now(self.tz).date()
        self.start_date = today - timedelta(today.weekday())
        self.parser = HTMLParser(target=Target())

    def get_schedule(self, channel, tz, search_imdb):
        ch_code = channel_code.get(channel)
        if ch_code is not  None:
            parser = self.parser
            schedule = Schedule(tz, self.tz, search_imdb)
            parser.target.schedule = schedule
            d = self.start_date
            base_url = 'http://www.gorod.lv/tv/'
            for i in range(7):
                schedule.set_date(d)
                url = base_url + ch_code + d.strftime('/%d.%m.%Y')
                fromstring(self.http.request(url)[1], parser)
                d += timedelta(1)
            return schedule.pop()


fetcher = Fetcher()


def get_schedule(channel, tz):
    return fetcher.get_schedule(channel, tz) or []
