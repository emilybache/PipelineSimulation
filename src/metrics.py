from datetime import timedelta
from itertools import tee, dropwhile

from dataclasses import dataclass

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


def _pairwise(iterable):
    "s -> (s0,s1), (s1,s2), (s2, s3), ..."
    a, b = tee(iterable)
    next(b, None)
    return zip(a, b)


def _average_timedelta(timedeltas):
    if not timedeltas:
        return None
    return sum(timedeltas, timedelta(0)) / len(timedeltas)


def pipeline_metrics(runs):
    lead_times = [run.end_time - run.start_time for run in runs if run.successful()]
    pipeline_failure_rate = (len(runs) - len(lead_times)) / len(runs)
    deployment_lead_times = [run.deploy_time - run.start_time for run in runs if run.deploy_time is not None]

    pipeline_interval = _interval([run.end_time for run in runs if run.successful()])
    deployment_interval = _interval([run.deploy_time for run in runs if run.deploy_time])

    pipeline_success_times = [run.end_time for run in runs if run.successful()]
    pipeline_failure_times = [run.end_time for run in runs if not run.successful()]
    pipeline_recovery_time = _recovery_time(pipeline_success_times, pipeline_failure_times)

    deployment_recovery_time = _recovery_time([run.deploy_time for run in runs if run.deploy_time], [])

    return PipelineMetrics(pipeline_lead_time=_average_timedelta(lead_times),
                           pipeline_failure_rate=pipeline_failure_rate,
                           pipeline_interval=pipeline_interval,
                           pipeline_recovery_time=pipeline_recovery_time,
                           deployment_lead_time=_average_timedelta(deployment_lead_times),
                           deployment_failure_rate=0.0,
                           deployment_interval=deployment_interval,
                           deployment_recovery_time=deployment_recovery_time
                           )


def _interval(end_times):
    intervals = [(t2-t1) for (t1, t2) in _pairwise(end_times)]
    return _average_timedelta(intervals)


def _recovery_time(success_times, failure_times):
    recovery_times = []
    for end_time in failure_times:
        following_successes = dropwhile(lambda t:t < end_time, success_times)
        if following_successes:
            recovery_times.append(next(following_successes) - end_time)
    if recovery_times:
        return _average_timedelta(recovery_times)
    else:
        return None

