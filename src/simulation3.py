from datetime import datetime, timedelta

from commits import generate_commits, generate_commits_to_deadline, generate_commits_to_weekly_deadline
from deploy import DeployPolicy, Deployer
from export import print_metrics
from metrics import pipeline_metrics
from simulation import run_simulation, print_runs

from stages import Stage

stages = [
    Stage("Build & Unit Test", duration=timedelta(minutes=15), failure_rate = 0),
    Stage("GUI Test", duration=timedelta(minutes=50), failure_rate = 0),
    Stage("Manual Test", duration=timedelta(minutes=120), failure_rate = 0, manual_stage=True),
]

start_time = datetime(year=2017,month=1,day=2,hour=8)

deployer=Deployer(duration=timedelta(minutes=20), deploy_policy=DeployPolicy.OnceAWeek, deploy_hour=8, deploy_day=3)

commits = generate_commits_to_weekly_deadline(100, start_time, 3)

runs = run_simulation(start_time, stages, commits=commits, deployer=deployer)
print_runs("simulation3", stages, runs)

metrics = pipeline_metrics(runs)
print_metrics("simulation3", metrics)
print(metrics.pretty_print())
