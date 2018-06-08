import pytest

from datetime import timedelta, datetime

from commits import Commit
from pipeline import *
from stages import Stage, StageStatus, StageRun


@pytest.fixture
def passing_stage():
    return Stage("Build", timedelta(minutes=10), failure_rate=0)

@pytest.fixture
def second_passing_stage():
    return Stage("AcceptanceTest", timedelta(minutes=10), failure_rate=0)

@pytest.fixture
def failing_stage():
    return Stage("Build", timedelta(minutes=10), failure_rate=1)

@pytest.fixture
def manual_stage():
    return Stage("Manual Test", timedelta(minutes=60), failure_rate=0, manual_stage=True)

@pytest.fixture
def scheduled_stage():
    return Stage("Manual Test", timedelta(minutes=60), failure_rate=0, manual_stage=True,
                 fixed_interval=timedelta(days=1))


now = datetime(year=2018,month=4,day=3,hour=8)
commit1 = Commit("#001", time=now - timedelta(minutes=10))
commit2 = Commit("#002", time=now - timedelta(minutes=5))
commit3 = Commit("#003", time=now + timedelta(minutes=5))


def test_str():
    assert "Pipeline Run(2018-04-03 08:00:00, 2018-04-03 08:10:00, [Commit(name='#001', time=datetime.datetime(2018, 4, 3, 7, 50))], [ok], )"\
           == str(PipelineRun(start_time=now,
                       end_time=now + timedelta(minutes=10),
                       changes_included=[commit1],
                       stage_results=[StageRun(StageStatus.ok)],
                       deploy_time="",
                       ))

def test_one_stage(passing_stage):
    stages = [passing_stage]
    commits = [commit1]
    pipeline = Pipeline(stages, trigger="commits")
    runs = pipeline.simulation(now, commits, timedelta(minutes=60))
    assert len(runs) == 1
    assert str(PipelineRun(start_time=now,
                        end_time=now + timedelta(minutes=10),
                        changes_included=commits,
                        stage_results=[StageRun(StageStatus.ok)],
                        deploy_time="",
                        )
               ) == str(runs[0])


def test_failing_stage(failing_stage):
    pipeline = Pipeline([failing_stage], trigger="commits")
    runs = pipeline.simulation(now, [commit1], timedelta(minutes=60))
    assert str(PipelineRun(start_time=now,
                        end_time=now + timedelta(minutes=10),
                        changes_included=[commit1],
                        stage_results=[StageStatus.fail],
                        deploy_time="",
                        )
               ) == str(runs[0])


def test_three_stages(passing_stage, failing_stage, second_passing_stage):
    pipeline = Pipeline([passing_stage, failing_stage, second_passing_stage], trigger="commits")
    runs = pipeline.simulation(now, [commit1], timedelta(minutes=60))
    assert str(PipelineRun(start_time=now,
                        end_time=now + passing_stage.duration + failing_stage.duration,
                        changes_included=[commit1],
                        stage_results=[StageStatus.ok, StageStatus.fail, StageStatus.skip],
                        deploy_time="",
                        )
               ) == str(runs[0])


def test_triggers():
    assert ([commit1, commit2], [commit3]) == commits_in_next_run([commit1, commit2, commit3], now)
    assert ([commit1, commit2], []) == commits_in_next_run([commit1, commit2], now)
    new_now = now +timedelta(minutes=10)
    assert ([commit3], []) == commits_in_next_run([commit3], new_now)


def test_several_runs(passing_stage):
    commits = [commit1, commit2, commit3]
    stages = [passing_stage]
    pipeline = Pipeline(stages, trigger="commits")
    runs = pipeline.simulation(now, commits, timedelta(minutes=60))
    assert len(runs) == 2
    assert runs[1].start_time == now + passing_stage.duration
    assert runs[1].changes_included == [commit3]
    assert runs[1].stage_results[0].status == StageStatus.ok
    assert runs[1].end_time == now + passing_stage.duration + passing_stage.duration


def test_several_concurrent_runs(passing_stage, second_passing_stage):
    commits = [commit1, commit2, commit3]
    stages = [passing_stage, second_passing_stage]
    pipeline = Pipeline(stages, trigger="commits")
    runs = pipeline.simulation(now, commits, timedelta(minutes=60))
    assert len(runs) == 2
    assert runs[1].start_time == now + passing_stage.duration
    assert runs[1].changes_included == [commit3]
    assert runs[1].stage_results[0].status == StageStatus.ok
    assert runs[1].stage_results[1].status == StageStatus.ok
    assert runs[1].end_time == now + passing_stage.duration + passing_stage.duration + passing_stage.duration


def test_non_concurrent_stages(passing_stage, manual_stage):
    commits = [commit1, commit2, commit3]
    stages = [passing_stage, manual_stage]
    pipeline = Pipeline(stages, trigger="commits")
    runs = pipeline.simulation(now, commits, timedelta(minutes=60))
    assert len(runs) == 2
    assert runs[1].start_time == now + passing_stage.duration
    assert runs[1].changes_included == [commit3]
    assert runs[1].stage_results[0].status == StageStatus.ok
    assert runs[1].stage_results[1].status == StageStatus.busy
    assert runs[1].end_time == now + passing_stage.duration + passing_stage.duration


def test_manual_test_in_office_hours(passing_stage, manual_stage):
    commits = [commit1, commit2]
    stages = [passing_stage, manual_stage]
    # start late in the day so manual testing is skipped
    start_time = datetime(year=2018,month=4,day=3,hour=17, minute=59)
    pipeline = Pipeline(stages, trigger="commits")
    runs = pipeline.simulation(start_time, commits, timedelta(minutes=60))
    assert len(runs) == 1
    assert runs[0].start_time == start_time
    assert runs[0].stage_results[0].status == StageStatus.ok
    assert runs[0].stage_results[1].status == StageStatus.unavailable
    assert runs[0].end_time == start_time + passing_stage.duration


def test_future_commits_dont_trigger_run():
    commits = [commit1, commit2, commit3]
    stages = [Stage("Build", duration=timedelta(minutes=1), failure_rate=0)]
    pipeline = Pipeline(stages, trigger="commits")
    runs = pipeline.simulation(now, commits, timedelta(minutes=30))
    assert len(runs) == 2


def test_one_stage_with_deployment(passing_stage):
    stages = [passing_stage]
    commits = [commit1]
    deploy_delay = timedelta(minutes=1)
    pipeline = Pipeline(stages, deployer=Deployer(deploy_delay=deploy_delay, deploy_policy=DeployPolicy.EveryPassing))
    runs = pipeline.simulation(now, commits, timedelta(minutes=60))
    assert str(PipelineRun(start_time=now,
                        end_time=now + timedelta(minutes=10),
                        changes_included=commits,
                        stage_results=[StageStatus.ok],
                        deploy_time=str(now + passing_stage.duration + deploy_delay),
                        )
               ) == str(runs[0])

