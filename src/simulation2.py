from datetime import datetime, timedelta

from commits import generate_commits
from deploy import DeployPolicy, Deployer
from simulation import run_simulation, print_runs

from stages import Stage

stages = [
    Stage("Build & Unit Test", duration=timedelta(minutes=15), failure_rate = 0.05),
    Stage("GUI Test", duration=timedelta(minutes=30), failure_rate = 0.3),
    Stage("Manual Test", duration=timedelta(minutes=120), failure_rate = 0.3, manual_stage=True),
]

start_time = datetime(year=2017,month=6,day=19,hour=8)

commits = generate_commits(100, start_time, offset=1000, max_interval=200)

deployer=Deployer(duration=timedelta(minutes=20), deploy_policy=DeployPolicy.OnceADay, deploy_hour=8)

runs = run_simulation(start_time, stages, commits=commits, deployer=deployer)
print_runs("simulation2", stages, runs)
