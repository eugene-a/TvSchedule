import datetime
import json
import httplib2
import lxml.html
import pytz
from tv_schedule import schedule, dateutil


def need_channel_code():
    return True

channel_code = None

_source_tz = pytz.timezone('Europe/Kiev')
_URL = 'http://tv.ua/ajax/updateProgsOnChannel?date=%d.%m.%Y&channel='

_http = httplib2.Http()
_parser = lxml.html.HTMLParser()

_today = dateutil.tv_date_now(_source_tz)
_weekday_now = _today.weekday()
_daydelta = datetime.timedelta(1)


def get_summary(url):
    content = _http.request(url)[1]
    doc = lxml.html.document_fromstring(content)
    page = doc[1][9][0][1]
    if len(page) > 2:
        return page[2][2].text_content()


def get_schedule(channel, tz):
    ch_code = channel_code.get(channel)
    if ch_code is None:
        return []

    sched = schedule.Schedule(tz, _source_tz)
    summaries = {}
    url = _URL + ch_code
    d = _today
    for i in range(_weekday_now, 7):
        content = _http.request(d.strftime(url))[1].decode()
        html = json.loads(content)['html']
        if html[0] == '<':
            table = lxml.html.fragment_fromstring(html)
            sched.set_date(d)
            for row in table:
                t = row[0].text
                if '.' in t:
                    sched.set_time(row[0].text.replace('.', ':'))
                    a = row[1][0]
                    sched.set_title(a[0].text)
                    href = a.get('href')
                    if href is not None:
                        summary = summaries.get(href)
                        if summary is None:
                            summary = get_summary(href)
                            summaries[href] = summary

                        sched.set_summary(summary)
                d += _daydelta
    return sched.pop()
