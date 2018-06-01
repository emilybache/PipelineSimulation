
from datetime import datetime, timedelta
import csv
import sys
import os

from pipeline import *


def run_simulation(name, start_date, stages, max_commit_interval):
    now = start_date
    commits = generate_commits(100, now, min_interval=1, max_interval=max_commit_interval)
    pipeline = Pipeline(stages)

    runs = pipeline.simulation(start_time=now + timedelta(minutes=5),
                               commits=commits,
                               duration=timedelta(days=5))

    with open(name + ".csv", "w") as f:
        writer = csv.writer(f)
        for row in as_rows(pipeline, runs):
            writer.writerow(row)