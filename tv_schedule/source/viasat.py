from httplib2 import Http
from lxml.etree import HTMLParser, fromstring
from pytz import timezone

from schedule import Schedule
from dateutil import fromwin, parse_date

LOAD_CHANNEL_CODE = True
channel_code = None


class _Target:
    def set_schedule(self, schedule):
        self._schedule = schedule

    def start(self, tag, attrib):
        if tag == 'div':
            self._div_class = attrib.get('class')
        self._data_str = ''

    def data(self, data):
        self._data_str += data

    def end(self, tag):
        if tag == 'div':
            if self._div_class == 'day_front':
                date = parse_date(fromwin(self._data_str), '%a, %d. %b')
                self._schedule.set_date(date)
            elif self._div_class == 'progtime':
                self._schedule.set_time(self._data_str)
            elif self._div_class == 'descript':
                summary = self._data_str.lstrip().lstrip(':')
                self._schedule.set_summary(summary)
        elif tag == 'h3' and self._div_class == 'descript':
            title = self._data_str
            self._data_str = ''
            if len(title) > 0 and title[0] == '(' and title[-1] == ')':
                title = title[1: -1]
            title = title.rstrip()
            self._schedule.set_title(title)
            if title == 'Интерны':
                self._schedule.set_episode()

    def close(self):
        pass


_SOURCE_TZ = timezone('Europe/Riga')

_http = Http()
_parser = HTMLParser(target=_Target())


def get_schedule(channel, tz):
    ch_code = channel_code.get(channel)
    if ch_code is None:
        return []

    schedule = Schedule(tz, _SOURCE_TZ)
    _parser.target.set_schedule(schedule)

    url = 'http://www.viasat.lv/viasat0/tv-programma27/'       \
        'tv-programma28/_/all/0/' + ch_code + '/?viewweek=1'

    fromstring(_http.request(url)[1], _parser)
    return schedule.pop()
