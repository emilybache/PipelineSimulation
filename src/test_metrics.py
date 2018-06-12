from datetime import timedelta, datetime

import pytest

from commits import Commit
from pipeline import PipelineRun
from stages import Stage, StageRun, StageStatus

from metrics import pipeline_metrics, PipelineMetrics


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
    metrics = pipeline_metrics(runs)
    assert metrics.deployment_lead_time == timedelta(minutes=11)
    assert metrics.deployment_failure_rate == 0
    assert metrics.deployment_interval == timedelta(minutes=20)
    assert metrics.deployment_recovery_time == None


def test_str():
    metrics = PipelineMetrics(deployment_lead_time=timedelta(minutes=11),
                              deployment_failure_rate=0,
                              deployment_interval=timedelta(minutes=20),
                              deployment_recovery_time=None,
                              pipeline_lead_time=timedelta(minutes=10),
                              pipeline_interval=timedelta(minutes=20),
                              pipeline_failure_rate=0.33,
                              pipeline_recovery_time=timedelta(minutes=30))
    assert  """\
Pipeline Metrics
Deployment Interval: 20 minutes
Deployment Lead Time: 11 minutes
Deployment Recovery Time: N/A
Deployment Failure Rate: 0%

Release Candidate Interval: 20 minutes
Release Candidate Lead Time: 10 minutes
Release Candidate Recovery Time: 30 minutes
Release Candidate Failure Rate: 33%
""" == metrics.pretty_print()