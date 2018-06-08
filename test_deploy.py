from datetime import timedelta, datetime

from dataclasses import dataclass, field

from deploy import Deployer, DeployPolicy
from stages import StageStatus, StageRun

# this is a friday
now = datetime(year=2018,month=6,day=1,hour=9)

@dataclass
class StubPipelineRun:
    start_time: datetime
    end_time: datetime
    stage_results: list = field(default_factory=list)
    deploy_time: str = ""


def test_choose_runs_to_deploy():
    deploy_delay = timedelta(minutes=1)
    deployer = Deployer(deploy_delay=deploy_delay, deploy_policy=DeployPolicy.EveryPassing)
    runs = [StubPipelineRun(now, now, [StageRun(StageStatus.ok, end_time=now)])]
    deployer.add_deployments(runs)

    assert runs[0].deploy_time == now + deploy_delay


def test_choose_runs_to_deploy_once_a_week():
    deploy_delay = timedelta(hours=1)
    ten = timedelta(minutes=10)
    deployer = Deployer(deploy_delay=deploy_delay, deploy_policy=DeployPolicy.OnceAWeek, deploy_hour=9, deploy_day=6)
    runs = [StubPipelineRun(now, now, [StageRun(StageStatus.ok, end_time=now)]),
            StubPipelineRun(now + ten, now + ten, [StageRun(StageStatus.ok, end_time=(now + ten))])]
    deployer.add_deployments(runs)

    assert runs[0].deploy_time == ""
    # deploy on Saturday
    assert runs[1].deploy_time == datetime(year=2018, month=6, day=2, hour=9) + deploy_delay


def test_choose_runs_to_deploy_daily():
    deploy_delay = timedelta(hours=1)
    ten = timedelta(minutes=10)
    deployer = Deployer(deploy_delay=deploy_delay, deploy_policy=DeployPolicy.OnceADay, deploy_hour=14)
    runs = [StubPipelineRun(now, now, [StageRun(StageStatus.ok, end_time=now)]),
            StubPipelineRun(now + ten, now + ten, [StageRun(StageStatus.ok, end_time=(now + ten))])]
    deployer.add_deployments(runs)

    assert runs[0].deploy_time == ""
    # deploy on Monday
    assert runs[1].deploy_time == datetime(year=2018, month=6, day=4, hour=14) + deploy_delay


