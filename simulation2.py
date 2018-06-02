from datetime import datetime, timedelta

from simulation import run_simulation

from stages import Stage

stages = [
    Stage("Build & Unit Test", duration=timedelta(minutes=15), failure_rate = 0.02),
    Stage("GUI Test", duration=timedelta(minutes=30), failure_rate = 0.3),
    Stage("Manual Test", duration=timedelta(minutes=300), failure_rate = 0.3, manual_stage=True),
]

start_time = datetime(year=2018,month=5,day=7,hour=8)

run_simulation("simulation2", start_time, stages, max_commit_interval=200)
