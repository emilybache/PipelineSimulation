
from datetime import datetime, timedelta
import csv
import sys

from pipeline import *

stages = [
    Stage("Build & Unit Test", duration=timedelta(minutes=10), failure_rate = 0.05),
    Stage("System Test", duration=timedelta(minutes=20), failure_rate = 0.2),
    Stage("Manual Test", duration=timedelta(minutes=120), failure_rate = 0.1, allow_concurrent_builds=False),
]

now = datetime.now()

commits = generate_commits(100, now, min_interval=3, max_interval=120)

pipeline = Pipeline(stages)

runs = pipeline.simulation(start_time=now + timedelta(minutes=5),
                           commits=commits,
                           duration=timedelta(days=5))

writer = csv.writer(sys.stdout)
for row in as_rows(pipeline, runs):
    writer.writerow(row)

