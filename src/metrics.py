from datetime import timedelta
from itertools import tee, dropwhile

from dataclasses import dataclass

from util import OfficeHours


def pipeline_metrics(runs):
    return MetricsCalculator(runs).metrics()


@dataclass
class PipelineMetrics:
    pipeline_lead_time: timedelta = None
    pipeline_failure_rate: float = 0.0
    pipeline_interval: timedelta = None
    pipeline_recovery_time: timedelta = None
    deployment_lead_time: timedelta = None
    deployment_failure_rate: float = 0.0
    deployment_interval: timedelta = None
    deployment_recovery_time: timedelta = None

    def pretty_print(self):
        s = f"""\
Pipeline Metrics
Deployment Interval: {_pretty_time_delta(self.deployment_interval)}
Deployment Lead Time: {_pretty_time_delta(self.deployment_lead_time)}
Deployment Recovery Time: {_pretty_time_delta(self.deployment_recovery_time)}
Deployment Failure Rate: {_pretty_percent(self.deployment_failure_rate)}%

Release Candidate Interval: {_pretty_time_delta(self.pipeline_interval)}
Release Candidate Lead Time: {_pretty_time_delta(self.pipeline_lead_time)}
Release Candidate Recovery Time: {_pretty_time_delta(self.pipeline_recovery_time)}
Release Candidate Failure Rate: {_pretty_percent(self.pipeline_failure_rate)}%
"""
        return s


class MetricsCalculator:

    def __init__(self, runs):
        self.runs = runs
        self.office_hours = OfficeHours()
        self.deploys = [run for run in self.runs if run.deploy_time is not None]
        self.successful_runs = [run for run in runs if run.successful()]
        self.failed_runs = [run for run in runs if run.failed()]

    def metrics(self):
        deployment_lead_times = [run.deploy_time - run.start_time for run in self.deploys]
        successful_deploy_times = [run.deploy_time for run in self.deploys]
        deployment_interval = _interval(successful_deploy_times)
        deployment_recovery_time = _recovery_time(successful_deploy_times, [])

        lead_times = [run.end_time - run.start_time for run in self.successful_runs]
        pipeline_failure_rate = len(self.failed_runs) / len(self.runs)
        pipeline_success_times = [run.end_time for run in self.successful_runs]
        pipeline_failure_times = [run.end_time for run in self.failed_runs]
        pipeline_interval = _interval(pipeline_success_times, self.office_hours)
        pipeline_recovery_time = _recovery_time(pipeline_success_times, pipeline_failure_times, self.office_hours)

        return PipelineMetrics(pipeline_lead_time=_average_timedelta(lead_times),
                               pipeline_failure_rate=pipeline_failure_rate,
                               pipeline_interval=pipeline_interval,
                               pipeline_recovery_time=pipeline_recovery_time,
                               deployment_lead_time=_average_timedelta(deployment_lead_times),
                               deployment_failure_rate=0.0,
                               deployment_interval=deployment_interval,
                               deployment_recovery_time=deployment_recovery_time
                               )


def _pretty_percent(number):
    return "{0:g}".format(number*100)


def _pretty_time_delta(timedelta):
    if not timedelta:
        return "N/A"
    days = timedelta.days
    seconds = int(timedelta.seconds)
    hours, seconds = divmod(seconds, 3600)
    minutes, seconds = divmod(seconds, 60)
    if days > 0:
        return '%d days %d hours' % (days, hours)
    elif hours > 0:
        return '%d hours %d minutes' % (hours, minutes)
    elif minutes > 0:
        return '%d minutes' % (minutes,)
    else:
        return '%ds' % (seconds,)


def _pairwise(iterable):
    "s -> (s0,s1), (s1,s2), (s2, s3), ..."
    a, b = tee(iterable)
    next(b, None)
    return zip(a, b)


def _average_timedelta(timedeltas):
    if not timedeltas:
        return None
    return sum(timedeltas, timedelta(0)) / len(timedeltas)


def _interval(end_times, office_hours=None):
    intervals = _intervals(_pairwise(end_times), office_hours)
    return _average_timedelta(intervals)


def _intervals(pairs, office_hours):
    intervals = []
    for (t1, t2) in pairs:
        if office_hours:
            interval = office_hours.interval(t1, t2)
        else:
            interval = t2 - t1
        intervals.append(interval)
    return intervals


def _recovery_time(success_times, failure_times, office_hours=None):
    recovery_times = []
    for end_time in failure_times:
        following_successes = dropwhile(lambda t:t < end_time, success_times)
        try:
            next_success = next(following_successes)
            if next_success:
                if office_hours:
                    interval = office_hours.interval(end_time, next_success)
                else:
                    interval = next_success - end_time
                recovery_times.append(interval)
        except StopIteration:
            pass
    if recovery_times:
        return _average_timedelta(recovery_times)
    else:
        return None

