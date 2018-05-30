
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from numpy.random import choice, randint
from enum import Enum
import csv


class StageStatus(Enum):
    fail = "fail"
    ok = "ok"
    skip = "skip (previous failure)"
    busy = "skip (resource busy)"

    def __str__(self):
        return self.value


@dataclass
class Stage:

    name: str
    duration: timedelta
    failure_rate: int
    stage_runs: list = field(default_factory=list)
    allow_concurrent_builds: bool = True

    def add_result(self, now, previous_stage=None):
        result = None

        if not result and previous_stage and previous_stage.status != StageStatus.ok:
            result = StageRun(StageStatus.skip, now, now)

        if not result and self.stage_runs and not self.allow_concurrent_builds:
            previous_run = self.stage_runs[-1]
            if now < previous_run.end_time:
                result = StageRun(StageStatus.busy, now, now)

        if not result:
            states = [StageStatus.fail, StageStatus.ok]
            probability_distribution = [self.failure_rate, 1-self.failure_rate]
            status = choice(states, 1, p=probability_distribution)[0]
            result = StageRun(status, now, now+self.duration)

        self.stage_runs.append(result)
        return result


@dataclass(eq=True)
class StageRun:
    status: StageStatus
    start_time: datetime
    end_time: datetime


@dataclass
class Commit:
    name: str
    time: datetime


@dataclass
class PipelineRun:
    start_time: datetime
    end_time: datetime
    changes_included: list = field(default_factory=list)
    stage_results: list = field(default_factory=list)


@dataclass(eq=True)
class Pipeline:
    stages: list = field(default_factory=list)
    trigger: str = "commits"

    def simulation(self, start_time, commits, duration):
        result = []
        now = start_time
        future_commits = commits
        while future_commits \
                and (now < start_time + duration):
            now, commits_this_run, future_commits = commits_in_next_run(future_commits, now)
            stage_results = simulate_stage_results(self.stages, now)
            end_time = stage_results[-1].end_time

            run = PipelineRun(start_time=now,
                              end_time=end_time,
                              changes_included=commits_this_run,
                              stage_results=[result.status for result in stage_results],
                              )
            now = now + self.stages[0].duration
            result.append(run)

        return result


def simulate_stage_results(stages, now):
    results = []
    previous_result = None
    for stage in stages:
        result = stage.add_result(now, previous_result)
        results.append(result)
        previous_result = result
        now = previous_result.end_time
    return results


def as_rows(pipeline, runs):
    rows = []
    stages = [stage.name for stage in pipeline.stages]
    fieldnames = ["start_time",
                  "changes_included"] + stages + ["end_time"]
    rows.append(fieldnames)
    for run in runs:
        row = [run.start_time, run.changes_included]
        for stage in run.stage_results:
            row.append(str(stage))
        row.append(run.end_time)
        rows.append(row)
    return rows


def commits_in_next_run(commits, now):
    commits_next_run, new_commits = [], []
    for commit in commits:
        (commits_next_run if commit.time < now else new_commits).append(commit)
    return now, commits_next_run, new_commits


def generate_commits(count, now, min_interval, max_interval):
    commits = []
    for i in range(1,count+1):
        commit = Commit("#{num:03d}".format(num=i), now)
        now = now + timedelta(minutes=randint(min_interval, max_interval))
        commits.append(commit)
    return commits
