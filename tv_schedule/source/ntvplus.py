import datetime
import urllib.parse
import pytz
import httplib2
import lxml.html
from tv_schedule import dateutil, schedule


def need_channel_code():
    return True

channel_code = None

_source_tz = pytz.timezone('Europe/Moscow')
_daydelta = datetime.timedelta(1)

_URL = 'http://tv.akado.ru/channels/'

_parser = lxml.etree.HTMLParser(encoding='utf-8')


_URL = 'http://www.ntvplus.ru'
_CHAN_URL = '/channels/channel.xl?'

_http = httplib2.Http()


def _fetch(url):
    content = _http.request(_URL + url)[1]
    doc = lxml.html.fromstring(content)
    return doc[1][5][0][4][0][0]


def _parse_infoitem(li):
    text = li.text

    if len(li) > 0:
        return text[:-2], li[0].text

    colidx = text.find(':')
    if colidx < 0:
        return None, text

    return text[:colidx], text[colidx + 2:]


def _get_title_and_summary(url):
    item = _fetch(url)
    title = item[1].text
    summary = ''
    for li in item[3]:
        field, value = _parse_infoitem(li)
        if field == 'Оригинальное название':
            title = value
        else:
            if field in ('Рейтинг', 'Режиссер', 'В ролях'):
                summary += field + ': '
            summary += value + '\n'
    return title, summary + item[5].text


def _get_column(data, sched, cash, col):
    for clearfix in filter(lambda x: len(x[col]) > 0, data):
        event = clearfix[col][0]
        sched.set_time(event[0].text)
        h5 = event[1][0]
        if h5.tag != 'h5':
            h5 = h5.getnext()
        if len(h5) == 0:
            title = h5.text
            summary = h5.tail
            if summary:
                ts = (title + ' ' + summary).split(' - ', 1)
                if len(ts) < 2:
                    ts.append(None)
                title, summary = ts
        else:
            href = h5[0].get('href')
            query = urllib.parse.urlparse(href).query
            key = urllib.parse.parse_qs(query)['id'][0]
            title, summary = cash.get(key) or (None, None)
            if title is None:
                cash[id] = title, summary = _get_title_and_summary(href)
            sched.set_foreign_title()

        sched.set_title(title)
        if summary:
            sched.set_summary(summary)


def get_schedule(channel, tz):
    ch_code = channel_code.get(channel)
    if ch_code is None:
        return []

    cash = {}
    today = dateutil.tv_date_now(_source_tz)
    weekday_now = today.weekday()
    sched = schedule.Schedule(tz, _source_tz)
    arg = {'id': ch_code}

    d = today
    for i in range(weekday_now, 7):
        sched.set_date(d)
        arg['day'] = d.strftime('%d.%m.%Y')
        url = _CHAN_URL + urllib.parse.urlencode(arg)
        data = _fetch(url).get_element_by_id('tvguide')[0]
        for col in range(2):
            _get_column(data, sched, cash, col)
        d += _daydelta
    return sched.pop()
