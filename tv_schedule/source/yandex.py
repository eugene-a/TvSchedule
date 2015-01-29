import datetime
import os.path
import json
import lxml.etree
import httplib2
import pytz
from tv_schedule import schedule,  config


def need_channel_code():
    return True

channel_code = None

_source_tz = pytz.timezone('Europe/Kiev')
_BASE_URL = 'https://tv.yandex.ru'

_cacerts = os.path.join(os.path.dirname(__file__), 'ssl', 'cacerts.crt')
_http = httplib2.Http(ca_certs=_cacerts)
_parser = lxml.etree.HTMLParser(encoding='utf-8')

_today = datetime.datetime.now(_source_tz).date()
_weekday_now = _today.weekday()
_daydelta = datetime.timedelta(1)


def _fetch(path):
    try:
        url = _BASE_URL + path
        content = _http.request(url)[1]
        doc = lxml.etree.fromstring(content, _parser)
        return doc[1][0][1][0]
    except:
        with open(os.path.join(config.output(), 'content.html', 'wb')) as f:
            f.write(content)
        raise


_CLS_DETAILS = 'b-tv-program-details'
_CLS_DESCR = 'b-tv-program-description'


def get_summary(a):
    content = _fetch(a.get('href'))
    td = content[1][0][0]

    summary = ''
    d = next((x for x in td if x.get('class') == _CLS_DETAILS), None)
    if d is not None:
        for row in d[0]:
            summary += row[0].text + ' '
            val = row[1]
            summary += val.text or val[0].text
            summary += '\n'
        dnext = d.getnext()
        if dnext is not None and dnext.get('class') == _CLS_DESCR:
            descr = dnext[0]
            summary += descr[0].text
            if len(descr) > 1:
                summary += ' '
                dc = json.loads(descr[1].get('data-bem'))
                summary += dc['b-tv-cut-button']['content'][0]['content']
            summary += '\n'
    return summary


def get_schedule(channel, tz):
    ch_code = channel_code.get(channel)
    if ch_code is None:
        return []

    sched = schedule.Schedule(tz, tz)
    summaries = {}
    d = _today
    for i in range(_weekday_now, 7):
        sched.set_date(d)
        path = '/87/channels/' + ch_code + d.strftime('?date=%Y-%m-%d')
        content = _fetch(path)
        items = content[2][0][0][0][0][0][0]
        if items.get('class') != 'tv-splash':
            for item in items:
                a = item[0]
                sched.set_time(a[0].text)
                title = a[1].text
                sched.set_title(title)
                summary = summaries.get(title)
                if summary is None:
                    summary = get_summary(a)
                    summaries[title] = summary

                if summary:
                    sched.set_summary(summary)
        d += _daydelta
    return sched.pop()
