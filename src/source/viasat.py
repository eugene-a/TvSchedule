from httplib2 import Http
from lxml.etree import HTMLParser, fromstring
from pytz import timezone

from schedule import Schedule
from dateutil import fromwin, parse_date

channel_code = {
    'VH1': '68',
    'TV1000': '977',
    'TV1000 Русское кино': '978',
    'TV1000 Action': '976',
    'Diva Universal': '24',
    'Travel Channel': '48',
    'Viasat History': '973',
    'TVCI': '104',
    'Cartoon Network': '87',
    'BBC World News': '80',
    'Disney XD': '907',
    'TV1000 Premium': '975',
}


class Target:
    def start(self, tag, attrib):
        if tag == 'div':
            self.div_class = attrib.get('class')
        self.data_str = ''

    def data(self, data):
        self.data_str += data

    def end(self, tag):
        if tag == 'div':
            if self.div_class == 'day_front':
                date = parse_date(fromwin(self.data_str), '%a, %d. %b')
                self.schedule.set_date(date)
            elif self.div_class == 'progtime':
                self.schedule.set_time(self.data_str)
            elif self.div_class == 'descript':
                summary = self.data_str.lstrip().lstrip(':')
                self.schedule.set_summary(summary)
        elif tag == 'h3' and self.div_class == 'descript':
            title = self.data_str
            self.data_str = ''
            if len(title) > 0 and title[0] == '(' and title[-1] == ')':
                title = title[1: -1]
            title = title.rstrip()
            self.schedule.set_title(title)
            if title == 'Интерны':
                self.schedule.set_episode()

    def close(self):
        pass


source_tz = timezone('Europe/Riga')
http = Http()
parser = HTMLParser(target=Target())


def get_schedule(channel, tz):
    ch_code = channel_code.get(channel)
    if ch_code is None:
        return []

    schedule = Schedule(tz, source_tz)
    parser.target.schedule = schedule
    url = 'http://www.viasat.lv/viasat0/tv-programma27/'       \
        'tv-programma28/_/all/0/' + ch_code + '/?viewweek=1'
    fromstring(http.request(url)[1], parser)
    return schedule.pop()
