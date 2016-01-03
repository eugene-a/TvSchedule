import urllib.parse
import pytz
import requests
import lxml.etree
from tv_schedule import schedule, dateutil


def need_channel_code():
    return False

_URL = 'http://2x2tv.ru'
_SCHED_URL = '/bitrix/components/tk/schedule/ajax.php'
_source_tz = pytz.timezone('Europe/Moscow')
_parser = lxml.etree.HTMLParser(encoding='utf-8')


def _fetch(url):
    url = urllib.parse.urljoin(_URL, url)
    resp = requests.get(url)
    doc = lxml.etree.fromstring(resp.content, _parser)
    return doc[1]


def _get_title_and_descr(url):
    body = _fetch(url)
    col = body[6][0][0][0][1][1][1][0][0]
#    table = col[0][0][0]
    text = col.getnext()[0]
    title, descr = None, ''
#    if len(table) < 10:
    title = text[1].text
#    else:
#        title = table[1][1].text
#        for i in [0, 3, 4, 5]:
#            descr += table[i][1].text + '\n'
    descr += '\n'.join(x.text or '' for x in text[2:])
    return title, descr


class _EventInfo:
    def __init__(self):
        self._cash = {}

    def get(self, row):
        url = row.get('onclick')
        if url is None:
            return None, ''

        url = url.split("'")[1]
        key = url[url.rindex('/', 0, -1) + 1: -1]
        title, descr = self._cash.get(key) or (None, None)
        if descr is None:
            self._cash[key] = title, descr = _get_title_and_descr(url)
        return title, descr


def get_schedule(channel, tz):
    if channel != '2x2':
        return []

    sched = schedule.Schedule(tz, _source_tz)
    event_info = _EventInfo()

    body = _fetch(_SCHED_URL)
    tab_list = body[1][0]
    days = (x[0] for x in tab_list)
    tabs = (x[0] for x in tab_list.getnext().getnext())

    for day, tab in zip(days, tabs):
        d = dateutil.parse_date(day[-2].text + day[-1].text, '%a%d %B')
        sched.set_date(d)
        for row in tab:
            it = row.iterchildren()
            time = next(it)[0][0].text
            title, descr = event_info.get(row)
            if title is None:
                next(it)
                title = next(it)[0].text
            if title is not None:
                sched.set_time(time)
                sched.set_title(title)
                sched.set_descr(descr)
    return sched.pop()
