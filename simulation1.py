
from datetime import datetime, timedelta

from simulation import run_simulation
from stages import Stage

stages = [
    Stage("Build & Unit Test", duration=timedelta(minutes=10), failure_rate = 0.05),
    Stage("System Test", duration=timedelta(minutes=20), failure_rate = 0.2),
    Stage("Manual Test", duration=timedelta(minutes=120), failure_rate = 0.1, manual_stage=True),
]

start_time = datetime(year=2018,month=5,day=7,hour=8)

run_simulation("simulation1", start_time, stages, max_commit_interval=100)
