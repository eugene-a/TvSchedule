import datetime


class Event:
    def __init__(self, dt):
        self.datetime = dt
        self.key = self.title = self.descr = None
        self.episode = False
        self.foreign_title = False

    def __eq__(self, other):
        if isinstance(other, Event):
            return self.datetime == other.datetime
        else:
            return id(self) == id(other)

    def __lt__(self, other):
        if isinstance(other, Event):
            return self.datetime < other.datetime
        else:
            return id(self) < id(other)

    def __str__(self):
        return self.datetime.strftime('%H:%M ') + self.title

_daydelta = datetime.timedelta(1)


class Schedule:
    def __init__(self, local_tz, source_tz):
        self._local_tz, self._source_tz = local_tz, source_tz
        self._events = []
        # a stored descr is used when an event is repeated later in a week
        self._cash = {}

    def set_date(self, d):
        self._source_date = d
        self._source_hour = 0

    def set_time(self, t, pm=False):
        hour, minute = (int(s) for s in t.split(':')[:2])
        if pm:
            hour += 12
        if hour < self._source_hour:
            self._source_date += _daydelta
        self._source_hour = hour
        time = datetime.time(hour, minute)
        dt = datetime.datetime.combine(self._source_date, time)
        return self.set_datetime(dt)

    def set_datetime(self, dt):
        dt = self._source_tz.localize(dt).astimezone(self._local_tz)
        self._events.append(Event(dt))
        return dt

    def set_title(self, title):
        if title is None:
            self._events.pop()
            return

        title = title.strip()

        event = self._events[-1]
        event.title = title.rstrip('.')
        i = title.find('"')
        if i < 0:
            event.key = title.strip('. ')
        else:
            event.key = title[i + 1: title.find('"', i + 1)]
        if event.descr is not None:
            self._cash[event.key] = event.descr

    def set_descr(self, descr):
        if descr:
            descr = descr.strip()
            if descr:
                event = self._events[-1]
                event.descr = descr
                if event.key is not None:
                    self._cash[event.key] = descr

    def set_episode(self):
        self._events[-1].episode = True

    def set_foreign_title(self):
        self._events[-1].foreign_title = True

    def pop(self):
        events = self._events
        for event in events:
            if event.descr is None:
                event.descr = self._cash.get(event.key)
        self._events = []
        self._cash.clear()
        return events
