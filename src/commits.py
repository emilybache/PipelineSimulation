from datetime import datetime, timedelta
from random import randint

from dataclasses import dataclass

from util import next_weekday, OfficeHours, next_day_of_week


@dataclass
class Commit:
    counter: int
    time: datetime

    @property
    def name(self):
        return "#{num:04d}".format(num=self.counter)

    def __str__(self):
        return self.name

    def __repr__(self):
        return "Commit(name='{}', time={})".format(self.name, self.time.__repr__())


def generate_commits(count, now, max_interval, offset=1):
    commits = []
    office_hours = OfficeHours()
    for i in range(offset, offset+count):
        commit = Commit(i, now)
        now = now + timedelta(minutes=randint(2, max_interval))
        now = skip_nights_and_weekends(now, office_hours)
        commits.append(commit)
    return commits


def generate_commits_to_weekly_deadline(count, now, weekday):
    commits = []
    next_release = next_day_of_week(now, weekday)
    offset = 1
    while next_release and len(commits) < count:
        more_commits = generate_commits_to_deadline(count - len(commits), now, deadline=next_release, offset=offset)
        if not more_commits:
            break
        commits.extend(more_commits)
        if commits:
            last_time = commits[-1].time
        else:
            last_time = now
        now = next_release
        next_release = next_day_of_week(last_time + timedelta(minutes=1), weekday)
        offset = commits[-1].counter
    return commits


def generate_commits_to_deadline(count, now, deadline, offset=1):
    office_hours = OfficeHours()
    commits = []
    for i in range(offset, offset+count):
        time_to_next_release = deadline - now
        min_interval = time_to_next_release/5
        max_interval = time_to_next_release
        if (max_interval - min_interval) < timedelta(minutes=5):
            break
        now = now + timedelta(seconds=randint(_total_seconds(min_interval), _total_seconds(max_interval)))
        now = skip_nights_and_weekends(now, office_hours)
        if now > deadline:
            break
        commit = Commit(i, now)
        commits.append(commit)

    return commits


def _total_seconds(t):
    return t.days*60*60*24 + t.seconds


def skip_nights_and_weekends(now, office_hours):
    if now.hour < office_hours.working_hour_start:
        return now.replace(hour=office_hours.working_hour_start)
    if now.hour >= office_hours.working_hour_end:
        return next_weekday(now).replace(hour=office_hours.working_hour_start)
    return now