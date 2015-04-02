import urllib.parse
import pytz
import httplib2
import lxml.etree
from tv_schedule import schedule, dateutil


def need_channel_code():
    return False

_URL = 'http://2x2tv.ru'
_SCHED_URL = '/bitrix/components/tk/schedule/ajax.php'
_source_tz = pytz.timezone('Europe/Moscow')
_http = httplib2.Http()
_parser = lxml.etree.HTMLParser(encoding='utf-8')


def _fetch(url):
    url = urllib.parse.urljoin(_URL, url)
    content = _http.request(url)[1]
    doc = lxml.etree.fromstring(content, _parser)
    return doc[1]


def _get_title_and_descr(url):
    info = _fetch(url)[1][0][1][2][0][0][2][0]
    table = info[0][0]
    div = info[-2]
    descr = ''
    if table.tag != 'table' or len(table) < 8:
        title = div[1].text
    else:
        title = table[1][1].text
        for i in [0, 3, 4, 5]:
            descr += table[i][1].text + '\n'
    return title, descr + div[2].tail.lstrip()


class _EventInfo:
    def __init__(self):
        self._cash = {}

    def get(self, a):
        href = a.get('href')
        key = href[href.rindex('/', 0, -1) + 1: -1]
        title, descr = self._cash.get(key) or (None, None)
        if descr is None:
            self._cash[key] = title, descr = _get_title_and_descr(href)
        return title, descr


def get_schedule(channel, tz):
    if channel != '2x2':
        return []

    sched = schedule.Schedule(tz, _source_tz)
    event_info = _EventInfo()

    tab_list = _fetch(_SCHED_URL)[0][1][0]
    days = (x[0] for x in tab_list[0][0])
    tabs = (x[0] for x in tab_list.getnext().getnext())

    for day, tab in zip(days, tabs):
        d = dateutil.parse_date(day[-2].text + day[-1].text, '%a%d %B')
        sched.set_date(d)
        for a in (x[0][0] for x in tab):
            it = a.iterchildren('div')
            sched.set_time(next(it)[-1].text)
            next(it)
            title, descr = event_info.get(a)
            if title is None:
                title = next(it)[0].text
            sched.set_title(title)
            sched.set_descr(descr)
    return sched.pop()
