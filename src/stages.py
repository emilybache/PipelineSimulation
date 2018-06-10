from enum import Enum
from numpy.random import choice, randint

from dataclasses import dataclass, field
from datetime import timedelta, datetime


class StageStatus(Enum):
    fail = "fail"
    repeat_fail = "fail"
    ok = "ok"
    skip = "skip (previous failure)"
    busy = "skip (resource busy)"
    unavailable = "skip (resource away)"

    def __str__(self):
        return self.value



@dataclass
class Stage:

    name: str
    duration: timedelta
    failure_rate: float
    stage_runs: list = field(default_factory=list)
    manual_stage: bool = False
    latest_hour: int = 18 # testers go home at this time
    single_threaded: bool = False

    def add_result(self, now, run_start_time, previous_stage=None):
        result = None

        if not result and previous_stage and previous_stage.status != StageStatus.ok:
            result = StageRun(StageStatus.skip, now, now)

        if not result and self.manual_stage and (now + self.duration).hour > self.latest_hour:
            result = StageRun(StageStatus.unavailable, now, now)

        if not result and self.stage_runs and (self.manual_stage or self.single_threaded):
            previous_run = self.stage_runs[-1]
            if now < previous_run.end_time:
                result = StageRun(StageStatus.busy, now, now)

        if not result and self.stage_runs and self.stage_runs[-1].status in (StageStatus.fail, StageStatus.repeat_fail):
            if run_start_time < self.stage_runs[-1].end_time: # havn't had time to submit a fix yet
                result = StageRun(StageStatus.repeat_fail, now, now+self.duration)

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
    start_time: datetime = None
    end_time: datetime = None

    def __str__(self):
        return str(self.status)

