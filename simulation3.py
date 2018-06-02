from datetime import datetime, timedelta

from deploy import DeployPolicy, Deployer
from simulation import run_simulation

from stages import Stage

stages = [
    Stage("Build & Unit Test", duration=timedelta(minutes=15), failure_rate = 0.02),
    Stage("GUI Test", duration=timedelta(minutes=50), failure_rate = 0.3),
    Stage("Manual Test", duration=timedelta(minutes=300), failure_rate = 0.3, manual_stage=True),
]

start_time = datetime(year=2018,month=5,day=7,hour=8)

deployer=Deployer(deploy_delay=timedelta(minutes=20), deploy_policy=DeployPolicy.OnceAWeek, deploy_hour=8, deploy_day=3)

run_simulation("simulation3", start_time, stages, max_commit_interval=200, deployer=deployer)
