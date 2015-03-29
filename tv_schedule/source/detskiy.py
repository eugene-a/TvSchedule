import datetime
import urllib.parse
import pytz
import httplib2
import lxml.html
from tv_schedule import schedule, dateutil


def need_channel_code():
    return False

_URL = 'http://telekanaldetskiy.ru'
_SCHED_URL = '/schedule_ajax_helper.php'
_sched_url = urllib.parse.urljoin(_URL, _SCHED_URL)
_headers = {'Content-Type': 'application/x-www-form-urlencoded'}
_source_tz = pytz.timezone('Europe/Moscow')
_daydelta = datetime.timedelta(1)
_http = httplib2.Http()
_parser = lxml.html.HTMLParser(encoding='utf-8')


def _get_descr(url):
    url = urllib.parse.urljoin(_URL, url)
    content = _http.request(url)[1]
    doc = lxml.html.fromstring(content, parser=_parser)
    descr = doc[1][1][0][2][0][1][3][2][0]
    for br in descr.iterchildren('br'):
        br.tail = '\n' + (br.tail or '')
    return descr.text_content()


class _Descriptions:
    def __init__(self):
        self._cash = {}

    def get(self, event):
        image = event[3][0]
        if image.tag != 'div':
            return image.getnext().text
        else:
            href = event[3][0][0].get('href')
            key = int(href[href.rindex('/') + 1:])
            descr = self._cash.get(key)
            if descr is None:
                self._cash[key] = descr = _get_descr(href)
            return descr


def get_schedule(channel, tz):
    if channel != 'Детский':
        return []

    today = dateutil.tv_date_now(_source_tz)
    weekday_now = today.weekday()
    sched = schedule.Schedule(tz, _source_tz)
    descriptions = _Descriptions()
    d = today
    for i in range(weekday_now, 7):
        sched.set_date(d)
        body = urllib.parse.urlencode({'d': d.strftime('%Y%m%d')})
        content = _http.request(_sched_url, 'POST', body, _headers)[1]
        doc = lxml.html.fragment_fromstring(content, True, parser=_parser)
        for event in doc[1]:
            sched.set_time(event[0].text)
            sched.set_title(event[2][0].text)
            sched.set_descr(descriptions.get(event))
        d += _daydelta
    return sched.pop()
