from datetime import datetime

from commits import generate_commits, skip_nights_and_weekends, generate_commits_to_deadline, \
    generate_commits_to_weekly_deadline
from util import OfficeHours, next_day_of_week


def test_generate_commits():
    start_time = datetime(year=2018,month=4,day=3,hour=9)
    commits = generate_commits(100, start_time, offset=1,max_interval=30)
    assert len(commits) == 100
    assert commits[0].name == "#0001"
    assert commits[0].time == start_time
    assert commits[-1].name == "#0100"


def test_generate_commits_during_working_hours():
    start_time = datetime(year=2018,month=4,day=3,hour=17, minute=59)
    commits = generate_commits(2, start_time, offset=1,max_interval=30)
    assert start_time < commits[1].time
    assert commits[1].time > datetime(year=2018,month=4,day=4,hour=8)


def test_skip_nights():
    start_time = datetime(year=2018,month=4,day=3,hour=18)
    next_time = skip_nights_and_weekends(start_time, OfficeHours())
    assert next_time == datetime(year=2018, month=4, day=4, hour=8)


def test_skip_weekends():
    friday = datetime(year=2018,month=6,day=1,hour=18)
    next_time = skip_nights_and_weekends(friday, OfficeHours())
    assert next_time == datetime(year=2018,month=6,day=4,hour=8)


def test_generate_commits_to_deadline():
    deadline = datetime(year=2018, month=6, day=1, hour=18)
    now = datetime(year=2018, month=6, day=1, hour=17)
    commits = generate_commits_to_deadline(10, now, deadline)
    assert len(commits) >= 1
    for commit in commits:
        assert commit.time < deadline
        assert commit.time >= now


def test_generate_commits_to_weekly_deadline():
    now = datetime(year=2018, month=6, day=14, hour=17)
    commits = generate_commits_to_weekly_deadline(10, now, 1)
    assert len(commits) <= 10

