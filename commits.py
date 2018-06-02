from datetime import datetime, timedelta
from random import randint

from dataclasses import dataclass


@dataclass
class Commit:
    name: str
    time: datetime

    def __str__(self):
        return self.name


def generate_commits(count, now, min_interval, max_interval, working_hour_start=8, working_hour_end=18):
    commits = []
    for i in range(1,count+1):
        commit = Commit("#{num:03d}".format(num=i), now)
        now = now + timedelta(minutes=randint(min_interval, max_interval))
        now = skip_nights(now, working_hour_start, working_hour_end)
        commits.append(commit)
    return commits


def skip_nights(now, working_hour_start, working_hour_end):
    if now.hour < working_hour_start or now.hour >= working_hour_end:
        now += timedelta(hours=24 - working_hour_end + working_hour_start)
    return now
