import datetime
import urllib.parse
import pytz
import httplib2
import lxml.etree
from tv_schedule import schedule, dateutil


def need_channel_code():
    return False

_URL = 'http://www.{}.tv/guides?'
_channels = {
    'Телепутешествия': 'teletravel',
    'Охотник и рыболов': 'ohotnikirybolov'
}
_source_tz = pytz.timezone('Europe/Moscow')
_daydelta = datetime.timedelta(1)
_http = httplib2.Http()
_parser = lxml.etree.HTMLParser(encoding='utf-8')


def get_schedule(channel, tz):
    chan = _channels.get(channel)
    if chan is None:
        return []

    base_url = _URL.format(chan)
    today = dateutil.tv_date_now(_source_tz, 0)
    weekday_now = today.weekday()
    sched = schedule.Schedule(tz, _source_tz)

    d = today
    for i in range(weekday_now, 7):
        sched.set_date(d)
        query = {'date': d.strftime('%Y-%m-%d')}
        url = base_url + urllib.parse.urlencode(query)

        content = _http.request(url)[1]
        doc = lxml.etree.fromstring(content, _parser)
        block_pr = doc[1][2][1][0][0][0][1][1]
        for event in block_pr:
            it = event.iterchildren()
            sched.set_time(next(it)[0].text)
            title = next(it)
            if len(title) > 0:
                title = title[1][0]
            sched.set_title(title.text.strip())
        d += _daydelta
    return sched.pop()
