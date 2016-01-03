import datetime
import urllib.parse
import pytz
import requests
import lxml.etree
from tv_schedule import dateutil, schedule


def need_channel_code():
    return True

channel_code = None

_source_tz = pytz.timezone('Europe/Moscow')
_daydelta = datetime.timedelta(1)

_parser = lxml.etree.HTMLParser()


_URL = 'http://www.ntvplus.ru'
_CHAN_URL = '/channels/channel.xl'


def _fetch(url, params=None):
    url = urllib.parse.urljoin(_URL, url)
    resp = requests.get(url, params)
    doc = lxml.etree.fromstring(resp.content, _parser)
    return doc[1][-2][0][4][0][0]


def _parse_infoitem(li):
    text = li.text

    if len(li) > 0:
        return text[:-2], li[0].text

    colidx = text.find(':')
    if colidx < 0:
        return None, text

    return text[:colidx], text[colidx + 2:]


def _get_title_and_descr(url):
    item = _fetch(url)
    title = item[1].text
    descr = ''
    for li in item[3]:
        field, value = _parse_infoitem(li)
        if field == 'Оригинальное название':
            title = value
        else:
            if field in ('Рейтинг', 'Режиссер', 'В ролях'):
                descr += field + ': '
            descr += value + '\n'
    return title, descr + (item[5].text or '')


class _EventInfo:
    def __init__(self):
        self._cash = {}

    def get(self, h5):
        href = h5[0].get('href')
        query = urllib.parse.urlparse(href).query
        key = int(urllib.parse.parse_qs(query)['id'][0])
        title, descr = self._cash.get(key) or (None, None)
        if title is None:
            self._cash[key] = title, descr = _get_title_and_descr(href)
        return title, descr


def _get_column(data, sched, event_info, col):
    for event in (x[col][0] for x in data if len(x[col]) > 0):
        sched.set_time(event[0].text)
        h5 = event[1][0]
        if h5.tag != 'h5':
            h5 = h5.getnext()
        if len(h5) > 0:
            title, descr = event_info.get(h5)
            sched.set_foreign_title()
        else:
            title = h5.text
            descr = h5.tail
            if descr:
                ts = (title + ' ' + descr).split(' - ', 1)
                if len(ts) < 2:
                    ts.append(None)
                title, descr = ts

        sched.set_title(title)
        if descr:
            sched.set_descr(descr)


def get_schedule(channel, tz):
    ch_code = channel_code.get(channel)
    if ch_code is None:
        return []

    event_info = _EventInfo()

    today = dateutil.tv_date_now(_source_tz)
    weekday_now = today.weekday()
    sched = schedule.Schedule(tz, _source_tz)
    params = {'id': ch_code}

    d = today
    for i in range(weekday_now, 7):
        sched.set_date(d)
        params['day'] = d.strftime('%d.%m.%Y')
        item = _fetch(_CHAN_URL, params)
        try:
            tvguide = next(x for x in item if x.get('id') == 'tvguide')
        except StopIteration:
            pass
        else:
            for col in range(2):
                _get_column(tvguide[0], sched, event_info, col)
        d += _daydelta
    return sched.pop()
