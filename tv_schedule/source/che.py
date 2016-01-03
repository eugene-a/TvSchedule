import datetime
import pytz
import requests
import lxml.html
from tv_schedule import schedule, dateutil

requests.packages.urllib3.disable_warnings()


def need_channel_code():
    return False

_URL = 'https://chetv.ru/teleprogramma/'
_source_tz = pytz.timezone('Europe/Moscow')
_parser = lxml.html.HTMLParser(encoding='utf-8')
_daydelta = datetime.timedelta(1)

_weekday = ['pon', 'vto', 'sre', 'cht', 'pyt', 'sub', 'vos']


def get_schedule(channel, tz):
    if channel != 'Че':
        return []

    today = dateutil.tv_date_now(_source_tz)
    weekday_now = today.weekday()
    sched = schedule.Schedule(tz, _source_tz)

    d = today
    for i in range(weekday_now, 7):
        sched.set_date(d)
        url = _URL + _weekday[i] + d.strftime('_%d_%m_%y/')

        r = requests.get(url, verify=False)
        doc = lxml.etree.fromstring(r.content, parser=_parser)
        items = doc[1][2][1][0][2][0][1][0][1][0][2]

        for right in (x[-1] for x in items):
            it = right.iterchildren()
            name = next(it)
            itn = name.iterchildren()
            sched.set_time(next(itn)[0][0][0].text)
            sched.set_title(next(itn).text)

            descr = ''

            try:
                next(itn)
                descr += next(itn).text + '\n'
            except StopIteration:
                pass

            descr += next(it)[0].text

            try:
                descr += '\n' + next(it).text_content()
            except StopIteration:
                pass

            sched.set_descr(descr)

        d += _daydelta

    return sched.pop()