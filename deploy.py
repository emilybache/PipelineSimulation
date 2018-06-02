from datetime import timedelta
from enum import Enum

from dataclasses import dataclass

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

    def deploy(self, now):
        if self.deploy_policy == DeployPolicy.EveryPassing and now.hour < self.latest_deploy_hour:
            return now + self.deploy_delay
        if self.deploy_policy == DeployPolicy.OnceADay:
            next_day = next_weekday(now)
            return next_day.replace(hour=self.deploy_hour) + self.deploy_delay
        if self.deploy_policy == DeployPolicy.OnceAWeek:
            next_deploy_day = next_day_of_week(now, self.deploy_day)
            return next_deploy_day + self.deploy_delay

        return ""


