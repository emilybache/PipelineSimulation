from datetime import timedelta
from enum import Enum

from dataclasses import dataclass
from itertools import groupby

from stages import StageStatus
from util import next_weekday, next_day_of_week


class DeployPolicy(Enum):
    EveryPassing = "Every Passing",
    OnceAWeek = "Once a Week"
    OnceADay = "Once a Day"
    NoDeploys= "No deploys"


@dataclass
class Deployer:
    deploy_policy: DeployPolicy = DeployPolicy.EveryPassing
    deploy_delay: timedelta = timedelta(minutes=2)
    deploy_hour: int = 0
    latest_deploy_hour: int = 16
    deploy_day: int = 1

    def _end_time(self, run):
        return run.stage_results[-1].end_time

    def _next_deploy_day(self, run):
        deploy_day = next_weekday(self._end_time(run))
        return deploy_day.replace(hour=self.deploy_hour, minute=0)

    def _next_deploy_weekday(self, run):
        deploy_day = next_day_of_week(self._end_time(run), self.deploy_day)
        return deploy_day.replace(hour=self.deploy_hour, minute=0)

    def add_deployments(self, runs):
        passing_runs = filter(lambda r: r.stage_results[-1].status == StageStatus.ok, runs)
        if self.deploy_policy == DeployPolicy.EveryPassing:
            for run in passing_runs:
                run.deploy_time = self._end_time(run) + self.deploy_delay

        if self.deploy_policy == DeployPolicy.OnceADay:
            # deploy only one run in each group, grouped by day
            for deploy_time, runs in groupby(passing_runs, self._next_deploy_day):
                the_one_to_deploy = list(runs)[-1]
                the_one_to_deploy.deploy_time = deploy_time + self.deploy_delay

        if self.deploy_policy == DeployPolicy.OnceAWeek:
            # deploy only one run in each group, grouped by week
            for deploy_time, runs in groupby(passing_runs, self._next_deploy_weekday):
                the_one_to_deploy = list(runs)[-1]
                the_one_to_deploy.deploy_time = deploy_time + self.deploy_delay


