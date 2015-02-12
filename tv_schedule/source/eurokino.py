import urllib.parse
import datetime
import pytz
import httplib2
import lxml.etree

from tv_schedule import schedule, dateutil


def need_channel_code():
    return False

_source_tz = pytz.timezone('Europe/Moscow')
_URL = 'http://eurokino.tv/schedule_ajax_helper.php'

_daydelta = datetime.timedelta(1)

_http = httplib2.Http()
_parser = lxml.etree.HTMLParser(encoding='utf-8')


def get_schedule(channel, tz):
    if channel != 'Еврокино':
        return []

    today = dateutil.tv_date_now(_source_tz)
    weekday_now = today.weekday()

    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    sched = schedule.Schedule(tz, _source_tz)

    d = today
    for i in range(weekday_now, 7):
        sched.set_date(d)
        body = urllib.parse.urlencode({'d': d.strftime("%Y%m%d")})

        content = _http.request(_URL, 'POST', body, headers)[1]
        doc = lxml.etree.fromstring(content, _parser)
        for event in doc[0][0]:
            sched.set_time(event[0].text)
            title = event[1][0].text
            summary = ''
            table = event[2][0][1][0][0]
            for row in table:
                field = row[0].text
                value = row[1][0].text
                if field == 'ориг.':
                    sched.set_foreign_title()
                    title = value
                else:
                    if field in ('режиссер', 'в ролях'):
                        summary += field + ': '
                    summary += value + '\n'
            summary += table.getnext().text
            sched.set_title(title)
            sched.set_summary(summary)
        d += _daydelta
    return sched.pop()
