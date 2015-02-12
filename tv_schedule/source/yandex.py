import datetime
import json
import pkg_resources
import lxml.etree
import httplib2
from tv_schedule import dateutil, schedule


def need_channel_code():
    return True

channel_code = None

_URL = 'https://tv.yandex.ru'
_CLS_DETAILS = 'b-tv-program-details'
_CLS_DESCR = 'b-tv-program-description'

_cacerts = pkg_resources.resource_filename(__name__, 'ssl/cacerts.crt')
_http = httplib2.Http(ca_certs=_cacerts)
_parser = lxml.etree.HTMLParser(encoding='utf-8')

_daydelta = datetime.timedelta(1)

_RETRY_COUNT = 3


def _fetch(path):
    url = _URL + path
    content = _http.request(url)[1]
    if len(content) > 0:
        # retry in the case of gateway timeout
        for i in range(_RETRY_COUNT):
            doc = lxml.etree.fromstring(content, _parser)
            cont = doc[1][0]
            if cont.tag == 'div':
                return cont[1][0]


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

    today = dateutil.tv_date_now(tz)
    weekday_now = today.weekday()

    sched = schedule.Schedule(tz, tz)
    cash = {}
    d = today
    for i in range(weekday_now, 7):
        sched.set_date(d)
        path = '/87/channels/' + ch_code + d.strftime('?date=%Y-%m-%d')
        content = _fetch(path)
        if content is not None:
            items = content[2][0][0][0][0][0][0]
            if items.get('class') != 'tv-splash':
                for item in items:
                    a = item[0]
                    sched.set_time(a[0].text)
                    title = a[1].text
                    sched.set_title(title)
                    summary = cash.get(title)
                    if summary is None:
                        summary = get_summary(a)
                        cash[title] = summary

                    if summary:
                        sched.set_summary(summary)
        d += _daydelta
    return sched.pop()
