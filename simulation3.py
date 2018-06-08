from datetime import datetime, timedelta

from commits import generate_commits
from deploy import DeployPolicy, Deployer
from simulation import run_simulation

from stages import Stage

stages = [
    Stage("Build & Unit Test", duration=timedelta(minutes=15), failure_rate = 0.1),
    Stage("GUI Test", duration=timedelta(minutes=50), failure_rate = 0.3),
    Stage("Manual Test", duration=timedelta(minutes=120), failure_rate = 0.3, manual_stage=True),
]

start_time = datetime(year=2017,month=1,day=2,hour=8)

deployer=Deployer(deploy_delay=timedelta(minutes=20), deploy_policy=DeployPolicy.OnceAWeek, deploy_hour=8, deploy_day=3)

commits = generate_commits(100, start_time, offset=1, max_interval=200)

run_simulation("simulation3", start_time, stages, commits=commits, deployer=deployer)
