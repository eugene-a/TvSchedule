import socket
import heapq
from http.client import HTTPException
from datetime import timedelta

from tzlocal import get_localzone

from config import Config
from util import genitive_month, prepare
from source import *


def info_value(show):
    return 0x10000 * show.episode + len(show.summary or '')

DEL_MAP = dict((ord(c), None) for c in '.,/-()" ')


def uniform(s):
    s = s.translate(DEL_MAP).lower()
    s = s.replace('год', 'г')
    s = s.replace('эпизод', '')
    return s.replace('эп', '')


TRESHOLD = timedelta(minutes=20)


def merge(shows):
    shows = heapq.merge(*shows)

    last = None
    for show in shows:
        if last is None:
            last = show
        else:
            if show == last:
                if show.title is not None and len(show.title) > len(last.title):
                    last.title = show.title
                if info_value(show) > info_value(last):
                    last.summary = show.summary
                if last.summary is not None:
                    if uniform(last.summary) == uniform(last.title):
                        last.summary = None
            elif show.key is not None:
                timediff = show.datetime - last.datetime
                if timediff < TRESHOLD or show.title not in last.title:
                    yield last
                    last = show
    if last is not None:
        yield last


class ScheduleWriter:
    def __init__(self, f_prog, f_sum):
        schedule_header = 'tv.all\n'
        f_prog.write(schedule_header)
        f_sum.write(schedule_header)

        self.tz = get_localzone()

        self.f_prog = f_prog
        self.f_sum = f_sum

        self.source = {'9 Канал Израиль':  (channel9, )}

        vse_ch = (
            'М1', 'OTV', '5 канал','Футбол+', 'ПлюсПлюс', 
            'НТН', 'К1', 'Спорт', 'Боец', 'НТВ+ Теннис',  'Fashion TV'
        )

        viasat_ch = (
            'VH1', 'Disney XD',
            'BBC World News', 'TV1000 Premium'
        )
        
        self.source.update((ch, (vsetv,)) for ch in vse_ch)
        self.source.update((ch, (viasat,)) for ch in viasat_ch)
 
    def find_schedule(self, channel, sources):
        if not isinstance(sources, tuple):
            sources = (sources,)
        for source in sources:
            shows = source.get_schedule(channel, self.tz)
            if len(shows) > 0:
                return shows
        return []


    def get_schedule(self, channel, sources):
        return merge([self.find_schedule(channel, s) for s in sources])


    def write(self, channel):
        sources = self.source.get(channel) or (vsetv, akado)

        last_date = None
        for show in self.get_schedule(channel, sources):
            date = show.datetime.date()
            if date != last_date:
                s = date.strftime('%A, %d %B').title()
                s = '\n' + genitive_month(s) + '. '
                show_date = s + channel + '\n'
                summary_date = s + '(Анонс)' + channel + '\n'
                self.f_prog.write(show_date)
                last_date = date
            show_str = str(show) + '\n'
            self.f_prog.write(show_str)
            summary = show.summary
            if summary is not None:
                if summary.startswith(show. title):
                    summary = summary[len(show.title):].lstrip('. ')
                if summary_date is not None:
                    self.f_sum.write(summary_date)
                    summary_date = None
                self.f_sum.write(show_str)
                self.f_sum.write(prepare(summary) + '\n')
        return last_date is not None


def open_output(name):
    return open(name, 'w', encoding='cp1251m', errors='replace')


def write_schedule(config_file):
    config = Config(config_file)

    with open_output(config.schedule()) as f_prog:
        with open_output(config.summaries()) as f_sum:
            with open(config.missing(), 'w', encoding='cp1251') as f_missing:
                writer = ScheduleWriter(f_prog, f_sum)
                with open(config.channels(), encoding='cp1251') as channels:
                    for line in channels:
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
