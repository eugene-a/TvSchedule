import re
import socket
import heapq
import os
import os.path
import http.client
import datetime
import contextlib

import tzlocal

from tv_schedule import config, source_import, dateutil

_CITYCAT = 'tv.all\n'
_KULICHKI = 'andgon\n'


def _title_score(event):
    title = event.title
    score = 0 if title.isupper() else len(title)
    return (event.foreign_title << 16) + score


def _info_score(event):
    return (event.episode << 16) + len(event.descr or '')

_del_map = dict((ord(c), None) for c in '.,/-()" ')


def _normalize(s):
    s = s.translate(_del_map).casefold()
    s = s.replace('год', 'г')
    s = s.replace('эпизод', '')
    return s.replace('эп', '')

_treshold = datetime.timedelta(minutes=20)


# combine info from multiple sources
def _merge(events):
    events = heapq.merge(*events)

    last = None
    for event in events:
        if last is None:
            last = event
        else:
            if event == last:
                if event.title is not None:
                    if _title_score(event) > _title_score(last):
                        last.title = event.title
                if _info_score(event) > _info_score(last):
                    last.descr = event.descr
                if last.descr is not None:
                    if _normalize(last.descr) == _normalize(last.title):
                        last.descr = None
            elif event.key is not None:
                # work around the case when multiple event in a source
                # are presented as a single event in another source
                timediff = event.datetime - last.datetime
                if timediff < _treshold or event.title not in last.title:
                    yield last
                    last = event
    if last is not None:
        yield last


# ListTV chokes if it encounters a date within text
# This can be avoided by replacing spaces separating day and month
# with something else
def _create_date_pattern():
    d = datetime.date(1900, 1, 1)
    gm = dateutil.genitive_month
    pattern = r'(\d{1,2}) +(' + '|'.join(
        (gm(d.replace(month=m).strftime('%B')) for m in range(1, 13))
    ) + ')'
    return re.compile(pattern, re.I | re.U)

_date_pattern = _create_date_pattern()
del _create_date_pattern


def _prepare_descr(s):
    s = s.strip()
    s = re.sub(r'\s+\n', '\n', s)               # remove trailing spaces
    s = re.sub(r'\n+', '\n', s)                 # remove empty lines
    s = re.sub(r'(\w)\n', r'\1.\n', s)          # end line with a period
    return re.sub(_date_pattern, r'\1-\2', s)   # dash between day and month


class _ScheduleWriter:
    def __init__(self, f_prog, f_sum):
        self._f_prog = f_prog
        self._f_sum = f_sum

        self._f_prog.write(_CITYCAT)
        self._f_sum.write(_KULICHKI)

        self._tz = tzlocal.get_localzone()

        self._source = {}

        sources = source_import.import_sources()
        self._default_source = sources.default

        for s in sources.special:
            self._source.update((ch, [s[0], ]) for ch in s[1])

    #  return the channel program from the first source found to have one
    def _find_schedule(self, channel, sources):
        if not isinstance(sources, list):
            sources = [sources, ]
        for source in sources:
            events = source(channel, self._tz)
            if len(events) > 0:
                return events
        return []

    def _get_schedule(self, channel, sources):
        return _merge([self._find_schedule(channel, s) for s in sources])

    def write(self, channel):
        sources = self._source.get(channel) or self._default_source

        last_date = None
        for event in self._get_schedule(channel, sources):
            date = event.datetime.date()
            if date != last_date:
                s = date.strftime('%A, %d %B').title()
                s = '\n' + dateutil.genitive_month(s) + '. '
                event_date = s + channel + '\n'
                descr_date = s + '(Анонс)' + channel + '\n'
                self._f_prog.write(event_date)
                last_date = date
            event_str = str(event) + '\n'
            self._f_prog.write(event_str)
            descr = event.descr
            if descr is not None:
                if descr.startswith(event. title):
                    descr = descr[len(event.title):].lstrip('. ')
                if descr_date is not None:
                    self._f_sum.write(descr_date)
                    descr_date = None
                self._f_sum.write(event_str)
                self._f_sum.write(_prepare_descr(descr) + '\n')
        return last_date is not None


# open a file with UTF-8-encoded text content for reading
def _open_r(name):
    return open(name, encoding='utf-8',)


# open a file for writing text data using CP1251 encoding
def _open_w(name):
    return open(name, 'w', encoding='cp1251', errors=None)


# same as _open_w
# but accepting and replacing characters outside of CP1251 character set
def _open_w_ext(name):
    return open(name, 'w', encoding='cp1251ext', errors='replace')


def write_schedule():
    output = config.output_dir()
    os.makedirs(output, exist_ok=True)

    schedule = os.path.join(output, 'schedule.txt')
    summaries = os.path.join(output, 'description.txt')
    missing = os.path.join(output, 'missing.txt')

    with contextlib.ExitStack() as stack:
        f_prog = stack.enter_context(_open_w_ext(schedule))
        f_sum = stack.enter_context(_open_w_ext(summaries))
        f_missing = stack.enter_context(_open_w(missing))

        writer = _ScheduleWriter(f_prog, f_sum)

        for line in config.channels():
            line = line.rstrip()
            print(line)
            try:
                result = writer.write(line[line.find('.') + 2:])
            except socket.error:
                result = False
            except http.client.HTTPException:
                result = False
            if not result:
                f_missing.write(line + '\n')
