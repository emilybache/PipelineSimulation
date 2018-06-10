
from datetime import timedelta

from pipeline import Pipeline
from export import to_csv


def run_simulation(start_date, stages, commits, deployer):
    now = start_date
    pipeline = Pipeline(stages, deployer=deployer)

    runs = pipeline.simulation(start_time=now + timedelta(minutes=5),
                               commits=commits,
                               duration=timedelta(days=21))
    return runs

def print_runs(name, stages, runs):
    to_csv(name, stages, runs)
