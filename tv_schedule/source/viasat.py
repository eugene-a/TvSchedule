import httplib2
import lxml.etree
import pytz

from tv_schedule import dateutil, schedule


def need_channel_code():
    return True

channel_code = None


class _Target:
    def set_schedule(self, sched):
        self._schedule = sched

    def start(self, tag, attrib):
        if tag == 'div':
            self._div_class = attrib.get('class')
        self._data_str = ''

    def data(self, data):
        self._data_str += data

    def end(self, tag):
        if tag == 'div':
            if self._div_class == 'day_front':
                date_str = dateutil.fromwin(self._data_str)
                date = dateutil.parse_date(date_str, '%a, %d. %b')
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


_source_tz = pytz.timezone('Europe/Riga')

_http = httplib2.Http()
_parser = lxml.etree.HTMLParser(target=_Target())


def get_schedule(channel, tz):
    ch_code = channel_code.get(channel)
    if ch_code is None:
        return []

    sched = schedule.Schedule(tz, _source_tz)
    _parser.target.set_schedule(sched)

    url = 'http://www.viasat.lv/viasat0/tv-programma27/'       \
        'tv-programma28/_/all/0/' + ch_code + '/?viewweek=1'

    lxml.etree.fromstring(_http.request(url)[1], _parser)
    return sched.pop()
