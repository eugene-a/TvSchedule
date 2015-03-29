import datetime
import urllib.parse
import itertools
import pytz
import httplib2
import lxml.etree
from tv_schedule import schedule, dateutil


def need_channel_code():
    return False

_URL = 'http://www.tvrus.eu/components/com_tvrus_eu/ajaxserver.php?'
_source_tz = pytz.timezone('CET')
_daydelta = datetime.timedelta(1)
_http = httplib2.Http()
_parser = lxml.etree.HTMLParser(encoding='utf-8')


def get_schedule(channel, tz):
    if channel != 'TVRUS':
        return []

    today = dateutil.tv_date_now(_source_tz)
    weekday_now = today.weekday()
    sched = schedule.Schedule(tz, _source_tz)

    query = {'action': 'programm'}
    d = today
    for i in range(weekday_now, 7):
        sched.set_date(d)
        query['date'] = d.strftime('%Y-%m-%d')
        url = _URL + urllib.parse.urlencode(query)
        content = _http.request(url)[1]
        doc = lxml.etree.fromstring(content, _parser)
        pmcontent = doc[0][0][0][0][1:]
        for event in itertools.chain(*(x[0][0] for x in pmcontent)):
            it = event.iterchildren()
            sched.set_time(next(it).text)
            sched.set_title(next(it).text.rstrip())
        d += _daydelta
    return sched.pop()
