from datetime import timedelta, datetime

import pytest

from commits import Commit
from pipeline import PipelineRun
from stages import Stage, StageRun, StageStatus

from metrics import pipeline_metrics, PipelineMetrics, _interval, MetricsCalculator, _pairwise, _intervals, \
    _average_timedelta


def test_passing_metrics():
    start_time = datetime(year=2017,month=12,day=11,hour=8)

    run1 = PipelineRun(start_time=start_time,
                end_time=start_time + timedelta(minutes=10),
                stage_results=[StageRun(StageStatus.ok)],
                )
    run2 = PipelineRun(start_time=start_time + timedelta(minutes=10),
                       end_time=start_time + timedelta(minutes=20),
                       stage_results=[StageRun(StageStatus.ok)],
                       )
    run3 = PipelineRun(start_time=start_time + timedelta(minutes=20),
                       end_time=start_time + timedelta(minutes=30),
                       stage_results=[StageRun(StageStatus.ok)],
                       )
    runs = [run1, run2, run3]
    metrics = pipeline_metrics(runs)
    assert metrics.pipeline_lead_time == timedelta(minutes=10)
    assert metrics.pipeline_failure_rate == 0.0
    assert metrics.pipeline_interval == timedelta(minutes=10)
    assert metrics.pipeline_recovery_time is None


def test_failing_metrics():
    start_time = datetime(year=2017,month=12,day=11,hour=8)

    run1 = PipelineRun(start_time=start_time,
                       end_time=start_time + timedelta(minutes=10),
                       stage_results=[StageRun(StageStatus.ok)],
                       )
    run2 = PipelineRun(start_time=start_time + timedelta(minutes=10),
                       end_time=start_time + timedelta(minutes=20),
                       stage_results=[StageRun(StageStatus.fail)],
                       )
    run3 = PipelineRun(start_time=start_time + timedelta(minutes=20),
                       end_time=start_time + timedelta(minutes=30),
                       stage_results=[StageRun(StageStatus.ok)],
                       )
    runs = [run1, run2, run3]
    metrics = pipeline_metrics(runs)
    assert metrics.pipeline_lead_time == timedelta(minutes=10)
    assert metrics.pipeline_failure_rate == pytest.approx(0.333, 0.01)
    assert metrics.pipeline_interval == timedelta(minutes=20)
    assert metrics.pipeline_recovery_time == timedelta(minutes=10)


def test_release_candidate_metrics_ignore_nights():
    start_time = datetime(year=2018,month=6,day=14,hour=17, minute=50)

    run1 = PipelineRun(start_time=start_time,
                       end_time=start_time + timedelta(minutes=10),
                       stage_results=[StageRun(StageStatus.ok)],
                       )
    run2 = PipelineRun(start_time=start_time + timedelta(minutes=10),
                       end_time=start_time + timedelta(minutes=20),
                       stage_results=[StageRun(StageStatus.fail)],
                       )
    run3 = PipelineRun(start_time=start_time + timedelta(hours=14, minutes=20),
                       end_time=start_time + timedelta(hours=14, minutes=30),
                       stage_results=[StageRun(StageStatus.ok)],
                       )
    runs = [run1, run2, run3]
    metrics = pipeline_metrics(runs)
    assert metrics.pipeline_lead_time == timedelta(minutes=10)
    assert metrics.pipeline_failure_rate == pytest.approx(0.333, 0.01)
    assert metrics.pipeline_interval == timedelta(minutes=20)
    assert metrics.pipeline_recovery_time == timedelta(minutes=10)


def test_release_candidate_metrics_ignore_weekends():
    start_time = datetime(year=2018,month=6,day=15,hour=17, minute=50)

    run1 = PipelineRun(start_time=start_time,
                       end_time=start_time + timedelta(minutes=10),
                       stage_results=[StageRun(StageStatus.ok)],
                       )
    run2 = PipelineRun(start_time=start_time + timedelta(minutes=10),
                       end_time=start_time + timedelta(minutes=20),
                       stage_results=[StageRun(StageStatus.fail)],
                       )
    run3 = PipelineRun(start_time=start_time + timedelta(days=2, hours=14, minutes=20),
                       end_time=start_time + timedelta(days=2, hours=14, minutes=30),
                       stage_results=[StageRun(StageStatus.ok)],
                       )
    runs = [run1, run2, run3]
    metrics = pipeline_metrics(runs)
    assert metrics.pipeline_lead_time == timedelta(minutes=10)
    assert metrics.pipeline_failure_rate == pytest.approx(0.333, 0.01)
    assert metrics.pipeline_interval == timedelta(minutes=20)
    assert metrics.pipeline_recovery_time == timedelta(minutes=10)


def test_deploy_metrics():
    start_time = datetime(year=2017,month=12,day=11,hour=8)

    run1 = PipelineRun(start_time=start_time,
                       end_time=start_time + timedelta(minutes=10),
                       stage_results=[StageRun(StageStatus.ok)],
                       deploy_time=start_time + timedelta(minutes=11)
                       )
    run2 = PipelineRun(start_time=start_time + timedelta(minutes=10),
                       end_time=start_time + timedelta(minutes=20),
                       stage_results=[StageRun(StageStatus.fail)],
                       )
    run3 = PipelineRun(start_time=start_time + timedelta(minutes=20),
                       end_time=start_time + timedelta(minutes=30),
                       stage_results=[StageRun(StageStatus.ok)],
                       deploy_time=start_time + timedelta(minutes=31)
                       )
    runs = [run1, run2, run3]
    calculator = MetricsCalculator(runs)
    metrics = calculator.metrics()
    assert metrics.deployment_lead_time == timedelta(minutes=11)
    assert metrics.deployment_failure_rate == 0
    assert metrics.deployment_interval == timedelta(minutes=20)
    assert metrics.deployment_recovery_time == None
    assert len(calculator.deploys) == 2


def test_deploy_metrics_recovery_doesnt_ignore_nights_and_weekends():
    start_time = datetime(year=2018,month=6,day=14,hour=17, minute=45)

    run1 = PipelineRun(start_time=start_time,
                       end_time=start_time + timedelta(minutes=10),
                       stage_results=[StageRun(StageStatus.ok)],
                       deploy_time=start_time + timedelta(minutes=11)
                       )
    run2 = PipelineRun(start_time=start_time + timedelta(minutes=10),
                       end_time=start_time + timedelta(minutes=20),
                       stage_results=[StageRun(StageStatus.fail)],
                       )
    run3 = PipelineRun(start_time=start_time + timedelta(hours=14, minutes=20),
                       end_time=start_time + timedelta(hours=14, minutes=30),
                       stage_results=[StageRun(StageStatus.ok)],
                       deploy_time=start_time + timedelta(hours=14, minutes=31)
                       )
    runs = [run1, run2, run3]
    metrics = pipeline_metrics(runs)
    assert metrics.deployment_lead_time == timedelta(minutes=11)
    assert metrics.deployment_failure_rate == 0
    assert metrics.deployment_interval == timedelta(hours=14, minutes=20)
    assert metrics.deployment_recovery_time == None


def test_str():
    metrics = PipelineMetrics(deployment_lead_time=timedelta(hours=11, minutes=5),
                              deployment_failure_rate=0,
                              deployment_interval=timedelta(days=1.25),
                              deployment_recovery_time=None,
                              pipeline_lead_time=timedelta(minutes=10),
                              pipeline_interval=timedelta(minutes=20),
                              pipeline_failure_rate=0.33,
                              pipeline_recovery_time=timedelta(minutes=30))
    assert  """\
Pipeline Metrics
Deployment Interval: 1 days 6 hours
Deployment Lead Time: 11 hours 5 minutes
Deployment Recovery Time: N/A
Deployment Failure Rate: 0%

Release Candidate Interval: 20 minutes
Release Candidate Lead Time: 10 minutes
Release Candidate Recovery Time: 30 minutes
Release Candidate Failure Rate: 33%
""" == metrics.pretty_print()


def test_deployment_interval():
    deploy_times = [datetime(year=2018,month=6,day=10,hour=17, minute=45),
                    datetime(year=2018,month=6,day=11,hour=17, minute=45),
                    datetime(year=2018,month=6,day=12,hour=17, minute=45),
                    datetime(year=2018,month=6,day=13,hour=17, minute=45),
                    datetime(year=2018,month=6,day=14,hour=17, minute=45)]
    assert timedelta(days=1) == _interval(deploy_times)


def test_deploy_interval():
    deploy_times = [datetime(2017, 12, 12, 7, 4),
                    datetime(2017, 12, 13, 7, 4),
                    datetime(2017, 12, 14, 7, 4),
                    datetime(2017, 12, 15, 7, 4),
                    datetime(2017, 12, 18, 7, 4),
                    datetime(2017, 12, 19, 7, 4),
                    datetime(2017, 12, 20, 7, 4),
                    datetime(2017, 12, 21, 7, 4),
                    datetime(2017, 12, 22, 7, 4)]
    pairs = [(datetime(2017, 12, 12, 7, 4), datetime(2017, 12, 13, 7, 4)),
            (datetime(2017, 12, 13, 7, 4), datetime(2017, 12, 14, 7, 4)),
            (datetime(2017, 12, 14, 7, 4), datetime(2017, 12, 15, 7, 4)),
            (datetime(2017, 12, 15, 7, 4), datetime(2017, 12, 18, 7, 4)),
            (datetime(2017, 12, 18, 7, 4), datetime(2017, 12, 19, 7, 4)),
            (datetime(2017, 12, 19, 7, 4), datetime(2017, 12, 20, 7, 4)),
            (datetime(2017, 12, 20, 7, 4), datetime(2017, 12, 21, 7, 4)),
            (datetime(2017, 12, 21, 7, 4), datetime(2017, 12, 22, 7, 4))]
    assert pairs == list(_pairwise(deploy_times))
    intervals = [timedelta(days=1), timedelta(days=1), timedelta(days=1),
                 timedelta(days=3),
                 timedelta(days=1), timedelta(days=1), timedelta(days=1), timedelta(days=1)]
    assert intervals == _intervals(pairs, None)
    assert _average_timedelta(intervals) == timedelta(days=(10/8.0))
    assert timedelta(days=(10/8.0)) == _interval(deploy_times)
