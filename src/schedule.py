from datetime import datetime, time, timedelta


class Show:
    def __init__(self, dt):
        self.datetime = dt
        self.key = self.title = self.summary = None
        self.episode = False

    def __eq__(self, other):
        if isinstance(other, Show):
            return self.datetime == other.datetime
        else:
            return id(self) == id(other)

    def __lt__(self, other):
        if isinstance(other, Show):
            return self.datetime < other.datetime
        else:
            return id(self) < id(other)

    def __str__(self):
        return self.datetime.strftime('%H:%M ') + self.title

_DAYDELTA = timedelta(1)


class Schedule:
    def __init__(self, local_tz, source_tz):
        self._local_tz, self._source_tz = local_tz, source_tz
        self._shows = []
        # a stored summary is used when the show is repeated later in a week
        self._summaries = {}

    def set_date(self, d):
        self._source_date = d
        self._source_hour = 0

    def set_time(self, t):
        hour, minute = (int(s) for s in t.split(':')[:2])
        if hour < self._source_hour:
            self._source_date += _DAYDELTA
        self._source_hour = hour
        dt = datetime.combine(self._source_date, time(hour, minute))
        # convert to local time zone
        dt = self._source_tz.localize(dt).astimezone(self._local_tz)
        self._shows.append(Show(dt))

    def set_title(self, title):
        if title is None:
            return

        show = self._shows[-1]
        show.title = title.rstrip('.')
        i = title.find('"')
        if i < 0:
            show.key = title.strip('. ')
        else:
            show.key = title[i + 1: title.find('"', i + 1)]
        if show.summary is not None:
            self._summaries[show.key] = show.summary

    def set_summary(self, summary):
        summary = summary.strip()
        if summary:
            show = self._shows[-1]
            show.summary = summary
            if show.key is not None:
                self._summaries[show.key] = summary

    def set_episode(self):
        self._shows[-1].episode = True

    def pop(self):
        shows = self._shows
        for show in shows:
            if show.summary is None:
                show.summary = self._summaries.get(show.key)
        self._shows = []
        self._summaries.clear()
        return shows
