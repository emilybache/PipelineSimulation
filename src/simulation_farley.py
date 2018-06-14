from datetime import datetime, timedelta

from commits import generate_commits
from deploy import DeployPolicy, Deployer
from export import print_metrics
from metrics import pipeline_metrics, MetricsCalculator
from simulation import run_simulation, print_runs
from stages import Stage

stages = [
    Stage("Commit Stage", duration=timedelta(minutes=3), failure_rate=0.005),
    Stage("Automated Acceptance Test", duration=timedelta(minutes=20), failure_rate=0.01),
    Stage("Performance Test", duration=timedelta(minutes=20), failure_rate=0.01),
    Stage("Internal Release", duration=timedelta(minutes=4), failure_rate=0.01, single_threaded=True),
]

start_time = datetime(year=2017,month=12,day=11,hour=8)

commits = generate_commits(100, start_time, offset=2000, max_interval=100)

deployer=Deployer(duration=timedelta(minutes=4), deploy_policy=DeployPolicy.OnceADay, deploy_hour=17, deploy_day=6)

runs = run_simulation(start_time, stages, commits=commits, deployer=deployer)
print_runs("simulation_farley", stages, runs)

metrics_calc = MetricsCalculator(runs)
metrics = metrics_calc.metrics()
print_metrics("simulation_farley", metrics)
print(metrics.pretty_print())
