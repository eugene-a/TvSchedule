import urllib.parse
import datetime
import requests
import lxml.html
import pytz
from tv_schedule import schedule, dateutil


def need_channel_code():
    return True

channel_code = None

_URL = 'http://tv.ua/ajax/updateProgsOnChannel'

_source_tz = pytz.timezone('Europe/Kiev')

_parser = lxml.html.HTMLParser()

_daydelta = datetime.timedelta(1)


def get_descr(url):
    resp = requests.get(url)
    doc = lxml.html.document_fromstring(resp.content)
    page = doc[1][9][0][1]
    if len(page) > 2:
        return page[2][2].text_content()


def get_schedule(channel, tz):
    ch_code = channel_code.get(channel)
    if ch_code is None:
        return []

    today = dateutil.tv_date_now(_source_tz)
    weekday_now = today.weekday()

    sched = schedule.Schedule(tz, _source_tz)
    cash = {}
    params = {'channel': ch_code}

    d = today
    for i in range(weekday_now, 7):
        params['date'] = d.strftime('%d.%m.%Y')
        resp = requests.get(_URL, params)
        html = resp.json()
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
                        descr = cash.get(href)
                        if descr is None:
                            descr = get_descr(href)
                            cash[href] = descr

                        sched.set_descr(descr)
                d += _daydelta
    return sched.pop()
