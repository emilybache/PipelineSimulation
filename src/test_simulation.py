from datetime import timedelta, datetime

from commits import generate_commits
from deploy import Deployer, DeployPolicy
from simulation import run_simulation
from stages import Stage


def test_simulation():
    stages = [
        Stage("Build & Unit Test", duration=timedelta(minutes=10), failure_rate = 0.02),
        Stage("System Test", duration=timedelta(minutes=20), failure_rate = 0.2),
        Stage("Performance Test", duration=timedelta(minutes=120), failure_rate = 0.1, single_threaded=True),
    ]

    start_time = datetime(year=2017,month=12,day=11,hour=8)
    commits = generate_commits(100, start_time, offset=2000, max_interval=100)
    deployer=Deployer(duration=timedelta(minutes=2), deploy_policy=DeployPolicy.EveryPassing)
    runs = run_simulation(start_time, stages, commits=commits, deployer=deployer)
    assert len(runs) <= 100