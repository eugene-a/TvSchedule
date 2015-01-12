from datetime import datetime, time, timedelta


class Show:
    def __init__(self, datetime):
        self.datetime = datetime
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


class Schedule:
    def __init__(self, local_tz, source_tz):
        self.local_tz, self.source_tz = local_tz, source_tz
        self.shows = []
        #a stored summary is used when the show is repeated later in a week
        self.summaries = {}

    def set_date(self, date):
        self.source_date = date
        self.source_hour = 0

    def set_time(self, t):
        hour, minute = (int(s) for s in t.split(':')[:2])
        if hour < self.source_hour:
            self.source_date += timedelta(1)
        self.source_hour = hour
        dt = datetime.combine(self.source_date, time(hour, minute))
        #convert to local time zone
        dt = self.source_tz.localize(dt).astimezone(self.local_tz)
        self.shows.append(Show(dt))

    def set_title(self, title):
        if title is None:
            return
            
        show = self.shows[-1]
        show.title = title.rstrip('.')
        i = title.find('"')
        if i < 0:
            show.key = title.strip('. ')
        else:
            show.key = title[i + 1: title.find('"', i + 1)]
        if show.summary is not None:
            self.summaries[show.key] = show.summary

    def set_summary(self, summary):
        summary = summary.strip()
        if summary:
            show = self.shows[-1]
            show.summary = summary
            if show.key is not None:
                self.summaries[show.key] = summary
                
    def set_episode(self):
        self.shows[-1].episode = True

    def pop(self):
        shows = self.shows
        for show in shows:
            if show.summary is None:
                show.summary = self.summaries.get(show.key)
        self.shows = []
        self.summaries.clear()
        return shows

