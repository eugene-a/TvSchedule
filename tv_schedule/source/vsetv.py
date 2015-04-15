import datetime
import urllib.parse
import lxml.etree
import httplib2
import pytz

from tv_schedule import dateutil, schedule


def need_channel_code():
    return True

channel_code = None

_source_tz = pytz.timezone('Europe/Kiev')
_headers = {
    'user-agent':
    'Mozilla/5.0 (Windows NT 6.2; WOW64; rv:22.0) Gecko/20100101 Firefox/22.0'
}

_URL = 'http://www.vsetv.com/'

_http = httplib2.Http()
_parser = lxml.etree.HTMLParser()


def _fetch(url):
    url = urllib.parse.urljoin(_URL, url)
    content = _http.request(url, headers=_headers)[1]
    return lxml.etree.fromstring(content, _parser)


def main(doc):
    return doc[3][6][3][0]


def _get_title_and_descr(url):
    doc = _fetch(url)
    foreign_title = False
    title = doc[0][0].text
    if title[-1] == ')':
        foreign_title = True
        title = title[title.rindex('(') + 1: -1]
    else:
        title = title[title.index('|') + 3:]

    table = main(doc)[1]
    if table.get('id') is None:
        return title, foreign_title, None

    descr = ''

    row = table[0]

    elem = row[0][0]
    if elem.tail is not None:
        descr += elem.tail + '\n'

    elem = elem.getnext().getnext()
    if elem.tail is None:
        elem = elem.getnext()
    descr += elem.tail.lstrip()

    elem = elem.getnext()
    if elem.tag == 'strong':
        descr += elem.text

    descr += '\n'

    row = row.getnext()
    for elem in row[0]:
        if elem.tag == 'br':
            descr += '\n'
        elif elem.tag == 'div':
            descr += elem.findtext('span')
            break
        else:
            descr += elem.text + elem.tail

    return title, foreign_title, descr


class _EventInfo:
    def __init__(self):
        self._cash = {}

    def get(self, a, quick):
        url = a.get('href')
        key = url[: url.find('.')]
        title, foreign_title, descr = (
            self._cash.get(key) or (None, False, None)
        )
        if title is None:
            if quick:
                title = a.text
            else:
                self._cash[key] = title, foreign_title, descr = (
                    _get_title_and_descr(url)
                )
        return title, foreign_title, descr

# don't load summaries for past shows
_elapsed_limit = datetime.timedelta(hours=4)


def get_schedule(channel, tz):
    ch_code = channel_code.get(channel)
    if ch_code is None:
        return []

    url = 'schedule_channel_' + ch_code + '_week.html'

    sched = schedule.Schedule(tz, _source_tz)
    event_info = _EventInfo()
    doc = _fetch(url)
    for div in main(doc)[6:]:
        if div.get('class') == 'sometitle':
            date = dateutil.parse_date(div[0][0][0].text, '%A, %d %B')
            sched.set_date(date)
        else:
            for subd in div:
                subd_class = subd.get('class')
                if subd_class == 'time':
                    now = datetime.datetime.now(tz)
                    elapsed = now - sched.set_time(subd.text)
                elif subd_class == 'prname2':
                    a = subd.find('a')
                    if a is None:
                        title = (
                            subd.text if len(subd) == 0 else subd[-1].tail[1:]
                        )
                        sched.set_title(title)
                    else:
                        title, foreign_title, descr = (
                            event_info.get(a, elapsed > _elapsed_limit)
                        )
                        sched.set_title(title)
                        if foreign_title:
                            sched.set_foreign_title()
                        if descr:
                            sched.set_descr(descr)
    return sched.pop()
