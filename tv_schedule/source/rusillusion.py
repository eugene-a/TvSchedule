import datetime
import urllib.parse
import pytz
import requests
import lxml.etree
from tv_schedule import schedule, dateutil


def need_channel_code():
    return False

_source_tz = pytz.timezone('Europe/Moscow')
_URL = 'http://russkiyillusion.ru'
_SCHED_URL = '/schedule_ajax_helper.php'

_daydelta = datetime.timedelta(1)

_parser = lxml.etree.HTMLParser(encoding='utf-8')


def _get_descr(url):
    url = urllib.parse.urljoin(_URL, url)
    resp = requests.get(url)
    doc = lxml.etree.fromstring(resp.content, _parser)
    text = doc[1][1][0][3][0][0][0][2]
    txt = text[0].text
    descr = txt + '\n' if txt else ''
    for row in text[1]:
        field = row[0].text
        value = row[1].text
        if field in ('Режиссер:', 'В ролях:'):
            descr += field + ' '
        descr += value + '\n'
    return descr


class _Descriptions:
    def __init__(self):
        self._cash = {}

    def get(self, a):
        href = a.get('href')
        key = int(href[href.rindex('/') + 1:])
        descr = self._cash.get(key)
        if descr is None:
            self._cash[key] = descr = _get_descr(href)
        return descr


def get_schedule(channel, tz):
    if channel != 'Русский иллюзион':
        return []

    descriptions = _Descriptions()

    today = dateutil.tv_date_now(_source_tz)
    weekday_now = today.weekday()
    sched = schedule.Schedule(tz, _source_tz)

    url = urllib.parse.urljoin(_URL, _SCHED_URL)

    d = today
    for i in range(weekday_now, 7):
        sched.set_date(d)
        data = {'d': d.strftime("%Y%m%d")}
        resp = requests.post(url, data)
        doc = lxml.etree.fromstring(resp.content, _parser)
        for row in doc[0][1]:
            sched.set_time(row[0].text)
            sched.set_title(row[1][0].text)
            descr = descriptions.get(row[2][0][0][0][0])
            sched.set_descr(descr)
        d += _daydelta
    return sched.pop()
