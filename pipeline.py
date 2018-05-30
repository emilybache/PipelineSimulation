
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from numpy.random import choice
from enum import Enum
import csv


class StageStatus(Enum):
    fail = "fail"
    ok = "ok"
    skip = "skip (previous failure)"

    def __str__(self):
        return self.value


@dataclass
class Stage:

    name: str
    duration: timedelta
    failure_rate: int
    allow_concurrent_builds: bool = True

    def result(self):
        states = [StageStatus.fail, StageStatus.ok]
        probability_distribution = [self.failure_rate, 1-self.failure_rate]
        return choice(states, 1, p=probability_distribution)[0]


@dataclass
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
    changes_included: field(default_factory=list)
    stage_results: field(default_factory=list)
    end_time: datetime


@dataclass(eq=True)
class Pipeline:

    stages: field(default_factory=list)
    trigger: str

    def simulation(self, start_time, commits, duration):
        result = []
        now = start_time
        future_commits = commits
        previous_run = None
        while future_commits and now < start_time + duration:
            commits_this_run, future_commits = commits_in_next_run(future_commits, now)
            stage_results = simulate_stage_results(self.stages, now)
            end_time = stage_results[-1].end_time

            run = PipelineRun(start_time=now,
                              changes_included=commits_this_run,
                              stage_results=[result.status for result in stage_results],
                              end_time=end_time)
            now = now + self.stages[0].duration
            result.append(run)
            previous_run = run
        return result


def simulate_stage_results(stages, now):
    results = []
    previous_result = None
    for stage in stages:
        if previous_result and previous_result.status == StageStatus.fail:
            results.append(StageRun(StageStatus.skip, start_time=now, end_time=now))
        else:
            results.append(StageRun(stage.result(), start_time=now, end_time=now+stage.duration))
        previous_result = results[-1]
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
    return commits_next_run, new_commits