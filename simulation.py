
from datetime import timedelta

from pipeline import Pipeline
from export import to_csv


def run_simulation(name, start_date, stages, commits, deployer):
    now = start_date
    pipeline = Pipeline(stages, deployer=deployer)

    runs = pipeline.simulation(start_time=now + timedelta(minutes=5),
                               commits=commits,
                               duration=timedelta(days=21))

    to_csv(name, pipeline, runs)
