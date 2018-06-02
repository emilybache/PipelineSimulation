
from datetime import timedelta

from pipeline import Pipeline
from commits import generate_commits
from export import to_csv


def run_simulation(name, start_date, stages, max_commit_interval, deployer):
    now = start_date
    commits = generate_commits(100, now, min_interval=1, max_interval=max_commit_interval)
    pipeline = Pipeline(stages, deployer=deployer)

    runs = pipeline.simulation(start_time=now + timedelta(minutes=5),
                               commits=commits,
                               duration=timedelta(days=14))

    to_csv(name, pipeline, runs)
