from datetime import date, datetime, timedelta
from itertools import islice

from lxml.etree import HTMLParser, fromstring
from httplib2 import Http
from pytz import timezone

from schedule import Schedule
from util import extract_text
from source.channels.yandexch import channel_code

http = Http()
parser = HTMLParser()


# Get the document body subelement at a given index.
# Occasionally the document received does not contain the expected data.
# Determine it by checking the subelement tag and repeat the attempt.
def fetch(path, index, tag):
    url = 'http://tv.yandex.ru/' + path

    attempts = 3
    elem_tag = elem = content = None

    while elem_tag != tag and attempts > 0:
        if content is not None:
            print(tag, elem.tag)
            with open('content.html', 'wb') as f:
                f.write(content)
        content = http.request(url)[1]
        body = fromstring(content, parser)[1]
        elem = body[index]
        elem_tag = elem.tag

        attempts -= 1

    return elem


def get_summary(path):
    yclndr = fetch(path, 3, 'div')
    table = yclndr[0]
    details = table[2][2][0]
    it = islice(details[0][1].iter(), 4, None)
    h1 = table[3][2][0]
    summary = ''.join(map(extract_text, it)) + '\n' + h1.tail
    episode = h1.text is not None
    return summary, episode

EPISODES = (
    'Моя прекрасная няня',
    'Не родись красивой',
    'Ефросинья. Продолжение'
)

START_ORDINAL = date(1970, 1, 1).toordinal()

today = datetime.now(timezone('Europe/Kiev')).date()
monday = today - timedelta(today.weekday())
del today


def get_schedule(channel, tz):
    ch_code = channel_code.get(channel)
    if ch_code is None:
        return []

    pattern = '?day={0}&hour=11&period=24&channel={1}'

    schedule = Schedule(tz, tz)
    summaries = {}

    d = monday
    for i in range(7):
        schedule.set_date(d)
        day = d.toordinal() - START_ORDINAL
        path = pattern.format(day, ch_code)

        lpage = fetch(path, 7, 'table')  # l-page
        yclndr = lpage[0][0][2]     # YCalendar-c-CalendarEvents
        events = yclndr[0][0][1]
        if events[0].tag != 'div':
            return []

        for event in events:
            elem = event.find('div')
            a = elem[0]
            if a.tag == 'span':
                a = a[0]
                m = elem[1]
                title = (m if len(m) == 0 else m[0]).text
            else:
                last = elem[-1]
                title = last.text if last.tag == 'b' else last.tail.lstrip()
            schedule.set_time(a.text)
            schedule.set_title(title)

            summary = summaries.get(title)
            episode = False
            if summary is None:
                summary, episode = get_summary(a.get('href'))
                if not episode and title in EPISODES:
                    episode = True
                if summary and not episode:
                    summaries[title] = summary
            if summary:
                schedule.set_summary(summary, episode)

        d += timedelta(1)
    return schedule.pop()
