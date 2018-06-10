from datetime import timedelta, datetime

import pytest

from commits import Commit
from pipeline import PipelineRun
from stages import Stage, StageRun, StageStatus

from metrics import pipeline_metrics


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
