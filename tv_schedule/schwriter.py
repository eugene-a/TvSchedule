import re
import socket
import heapq
from os import makedirs
from http.client import HTTPException
from datetime import date, timedelta
from contextlib import ExitStack

from tzlocal import get_localzone

import config
from dateutil import genitive_month


def _info_value(show):
    return 0x10000 * show.episode + len(show.summary or '')

_DEL_MAP = dict((ord(c), None) for c in '.,/-()" ')


def _uniform(s):
    s = s.translate(_DEL_MAP).lower()
    s = s.replace('год', 'г')
    s = s.replace('эпизод', '')
    return s.replace('эп', '')


_TRESHOLD = timedelta(minutes=20)


# combine info from multiple sources
def _merge(shows):
    shows = heapq.merge(*shows)

    last = None
    for show in shows:
        if last is None:
            last = show
        else:
            if show == last:
                if show.title is not None:
                    if len(show.title) > len(last.title):
                        last.title = show.title
                if _info_value(show) > _info_value(last):
                    last.summary = show.summary
                if last.summary is not None:
                    if _uniform(last.summary) == _uniform(last.title):
                        last.summary = None
            elif show.key is not None:
                # work around the case when multiple shows in a source
                # are presented as a single show in another source
                timediff = show.datetime - last.datetime
                if timediff < _TRESHOLD or show.title not in last.title:
                    yield last
                    last = show
    if last is not None:
        yield last


# ListTV chokes if it encounters a date within text
# This can be avoided by replacing spaces separating day and month
# with something else
def _create_date_pattern():
    d = date(1900, 1, 1)
    gm = genitive_month
    pattern = r'(\d{1,2}) +(' + '|'.join(
        (gm(d.replace(month=m).strftime('%B')) for m in range(1, 13))
    ) + ')'
    return re.compile(pattern, re.I | re.U)

_DATE_PATTERN = _create_date_pattern()
del _create_date_pattern


def _prepare_summary(s):
    s = s.strip()
    s = re.sub(r'\s+\n', '\n', s)                      # remove trailing spaces
    s = re.sub(r'\n+', '\n', s)                         # remove empty lines
    s = re.sub(r'(\w)\n', r'\1.\n', s)              # end line with a period
    return re.sub(_DATE_PATTERN, r'\1-\2', s)  # dash between day and month


class _ScheduleWriter:
    def __init__(self, f_prog, f_sum):
        self._f_prog = f_prog
        self._f_sum = f_sum

        schedule_header = 'tv.all\n'
        self._f_prog.write(schedule_header)
        self._f_sum.write(schedule_header)

        self._tz = get_localzone()

        self._source = {}

        sources = config.get_sources()
        self._default_source = sources.default

        for s in sources.special:
            self._source.update((ch, [s[0], ]) for ch in s[1])

    #  return the channel program from the first source found to have one
    def _find_schedule(self, channel, sources):
        if not isinstance(sources, list):
            sources = [sources, ]
        for source in sources:
            shows = source(channel, self._tz)
            if len(shows) > 0:
                return shows
        return []

    def _get_schedule(self, channel, sources):
        return _merge([self._find_schedule(channel, s) for s in sources])

    def write(self, channel):
        sources = self._source.get(channel) or self._default_source

        last_date = None
        for show in self._get_schedule(channel, sources):
            date = show.datetime.date()
            if date != last_date:
                s = date.strftime('%A, %d %B').title()
                s = '\n' + genitive_month(s) + '. '
                show_date = s + channel + '\n'
                summary_date = s + '(Анонс)' + channel + '\n'
                self._f_prog.write(show_date)
                last_date = date
            show_str = str(show) + '\n'
            self._f_prog.write(show_str)
            summary = show.summary
            if summary is not None:
                if summary.startswith(show. title):
                    summary = summary[len(show.title):].lstrip('. ')
                if summary_date is not None:
                    self._f_sum.write(summary_date)
                    summary_date = None
                self._f_sum.write(show_str)
                self._f_sum.write(_prepare_summary(summary) + '\n')
        return last_date is not None


# open a file with UTF-8-encoded text content for reading
def _open_r(name):
    return open(name, encoding='utf-8',)


# open a file for writing text data  using CP1251 encoding
def _open_w(name):
    return open(name, 'w', encoding= 'cp1251', errors=None)


# same as _open_w
# but accepting and replacing characters outside of CP1251 character set
def _open_w_ext(name):
    return open(name, 'w', encoding='cp1251ext', errors='replace')


def write_schedule():
    makedirs(config.output_dir(), exist_ok=True)

    with ExitStack() as stack:
        f_channels = stack.enter_context( _open_r(config.channels()))
        f_prog = stack.enter_context(_open_w_ext(config.schedule()))
        f_sum = stack.enter_context(_open_w_ext(config.summaries()))
        f_missing = stack.enter_context(_open_w(config.missing()))
 
        writer = _ScheduleWriter(f_prog,  f_sum)
     
        for line in f_channels:
            line = line.rstrip()
            print(line)
            try:
                result = writer.write(line[line.find('.') + 2:])
            except socket.error:
                result = False
            except HTTPException:
                result = False
            if not result:
                f_missing.write(line + '\n')