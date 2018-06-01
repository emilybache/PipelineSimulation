from datetime import datetime, timedelta
from io import StringIO

import pytest

from pipeline import *


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
    return Stage("Manual Test", timedelta(minutes=60), failure_rate=0, allow_concurrent_builds=False)

now = datetime.now()
commit1 = Commit("#001", time=now - timedelta(minutes=10))
commit2 = Commit("#002", time=now - timedelta(minutes=5))
commit3 = Commit("#003", time=now + timedelta(minutes=5))


def test_one_stage(passing_stage):
    stages = [passing_stage]
    commits = [commit1]
    pipeline = Pipeline(stages, trigger="commits")
    runs = pipeline.simulation(now, commits, timedelta(minutes=60))
    assert [PipelineRun(start_time=now,
                        end_time=now + timedelta(minutes=10),
                        changes_included=commits,
                        stage_results=[StageStatus.ok],
                        )
            ] == runs


def test_failing_stage(failing_stage):
    pipeline = Pipeline([failing_stage], trigger="commits")
    runs = pipeline.simulation(now, [commit1], timedelta(minutes=60))
    assert [PipelineRun(start_time=now,
                        end_time=now + timedelta(minutes=10),
                        changes_included=[commit1],
                        stage_results=[StageStatus.fail],
                        )
            ] == runs


def test_stage_status_strings():
    assert str(StageStatus.ok) == "ok"
    assert ["ok", "fail", "foobar"] == list(map(str, [StageStatus.ok, StageStatus.fail, "foobar"]))


def test_stage_result(passing_stage, failing_stage):
    assert passing_stage.add_result(now, now) == StageRun(StageStatus.ok, now, now+passing_stage.duration)
    assert failing_stage.add_result(now, now) == StageRun(StageStatus.fail, now, now+failing_stage.duration)


def test_three_stages(passing_stage, failing_stage, second_passing_stage):
    pipeline = Pipeline([passing_stage, failing_stage, second_passing_stage], trigger="commits")
    runs = pipeline.simulation(now, [commit1], timedelta(minutes=60))
    assert [PipelineRun(start_time=now,
                        end_time=now + passing_stage.duration + failing_stage.duration,
                        changes_included=[commit1],
                        stage_results=[StageStatus.ok, StageStatus.fail, StageStatus.skip],
                        )
            ] == runs


def test_as_rows(passing_stage, failing_stage, second_passing_stage):
    pipeline = Pipeline([passing_stage, failing_stage, second_passing_stage], trigger="commits")
    runs = pipeline.simulation(now, [commit1], timedelta(minutes=60))
    rows = as_rows(pipeline, runs)
    assert ",".join(map(str,rows[0])) == "start_time,changes_included,Build,Build,AcceptanceTest,end_time"


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
    assert runs[1].stage_results == [StageStatus.ok]
    assert runs[1].end_time == now + passing_stage.duration + passing_stage.duration


def test_several_concurrent_runs(passing_stage, second_passing_stage):
    commits = [commit1, commit2, commit3]
    stages = [passing_stage, second_passing_stage]
    pipeline = Pipeline(stages, trigger="commits")
    runs = pipeline.simulation(now, commits, timedelta(minutes=60))
    assert len(runs) == 2
    assert runs[1].start_time == now + passing_stage.duration
    assert runs[1].changes_included == [commit3]
    assert runs[1].stage_results == [StageStatus.ok, StageStatus.ok]
    assert runs[1].end_time == now + passing_stage.duration + passing_stage.duration + passing_stage.duration


def test_non_concurrent_stages(passing_stage, manual_stage):
    commits = [commit1, commit2, commit3]
    stages = [passing_stage, manual_stage]
    pipeline = Pipeline(stages, trigger="commits")
    runs = pipeline.simulation(now, commits, timedelta(minutes=60))
    assert len(runs) == 2
    assert runs[1].start_time == now + passing_stage.duration
    assert runs[1].changes_included == [commit3]
    assert runs[1].stage_results == [StageStatus.ok, StageStatus.busy]
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
    assert runs[0].stage_results == [StageStatus.ok, StageStatus.unavailable]
    assert runs[0].end_time == start_time + passing_stage.duration


def test_generate_commits():
    start_time = datetime(year=2018,month=4,day=3,hour=9)
    commits = generate_commits(100, start_time, min_interval=5,max_interval=30)
    assert len(commits) == 100
    assert commits[0].name == "#001"
    assert commits[0].time == start_time
    assert commits[-1].name == "#100"


def test_generate_commits_during_working_hours():
    start_time = datetime(year=2018,month=4,day=3,hour=17, minute=59)
    commits = generate_commits(2, start_time, min_interval=5,max_interval=30)
    assert start_time < commits[1].time
    assert commits[1].time > datetime(year=2018,month=4,day=4,hour=8)


def test_next_day():
    start_time = datetime(year=2018,month=4,day=3,hour=18)
    next_time = skip_nights(start_time, 8, 18)
    assert next_time == datetime(year=2018, month=4, day=4, hour=8)


def test_future_commits_dont_trigger_run():
    commits = [commit1, commit2, commit3]
    stages = [Stage("Build", duration=timedelta(minutes=1), failure_rate=0)]
    pipeline = Pipeline(stages, trigger="commits")
    runs = pipeline.simulation(now, commits, timedelta(minutes=30))
    assert len(runs) == 2


def test_realistic_failure_recovery(passing_stage, failing_stage):
    end_of_first_stage_time = now+passing_stage.duration
    assert passing_stage.add_result(now, now) == StageRun(StageStatus.ok, now, end_of_first_stage_time)
    assert failing_stage.add_result(end_of_first_stage_time, now) == StageRun(StageStatus.fail, end_of_first_stage_time, end_of_first_stage_time+failing_stage.duration)
    start_of_next_pipeline = now + passing_stage.duration
    end_of_next_pipeline_first_stage = start_of_next_pipeline + passing_stage.duration
    assert passing_stage.add_result(start_of_next_pipeline, start_of_next_pipeline) == StageRun(StageStatus.ok, start_of_next_pipeline, end_of_next_pipeline_first_stage)
    assert failing_stage.add_result(end_of_next_pipeline_first_stage, start_of_next_pipeline) == StageRun(StageStatus.repeat_fail, end_of_next_pipeline_first_stage, end_of_next_pipeline_first_stage+failing_stage.duration)


