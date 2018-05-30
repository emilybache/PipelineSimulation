from datetime import datetime, timedelta
from io import StringIO

from pipeline import *

passing_stage = Stage("Build", timedelta(minutes=10), failure_rate=0)
failing_stage = Stage("Build", timedelta(minutes=10), failure_rate=1)
now = datetime.now()
commit1 = Commit("#001", time=now - timedelta(minutes=10))
commit2 = Commit("#002", time=now - timedelta(minutes=5))
commit3 = Commit("#003", time=now + timedelta(minutes=5))

def test_one_stage():
    stages = [passing_stage]
    commits = [commit1]
    pipeline = Pipeline(stages, trigger="commits")
    runs = pipeline.simulation(now, commits, timedelta(minutes=60))
    assert [PipelineRun(start_time=now,
                        changes_included=commits,
                        stage_results=[StageStatus.ok],
                        end_time=now + timedelta(minutes=10))
            ] == runs


def test_failing_stage():
    pipeline = Pipeline([failing_stage], trigger="commits")
    runs = pipeline.simulation(now, [commit1], timedelta(minutes=60))
    assert [PipelineRun(start_time=now,
                        changes_included=[commit1],
                        stage_results=[StageStatus.fail],
                        end_time=now + timedelta(minutes=10))
            ] == runs


def test_stageResult():
    assert str(StageStatus.ok) == "ok"


def test_stage_result():
    assert passing_stage.result() == StageStatus.ok
    assert failing_stage.result() == StageStatus.fail
    assert ["ok", "fail", "foobar"] == list(map(str, [StageStatus.ok, StageStatus.fail, "foobar"]))


def test_three_stages():
    pipeline = Pipeline([passing_stage, failing_stage, passing_stage], trigger="commits")
    runs = pipeline.simulation(now, [commit1], timedelta(minutes=60))
    assert [PipelineRun(start_time=now,
                        changes_included=[commit1],
                        stage_results=[StageStatus.ok, StageStatus.fail, StageStatus.skip],
                        end_time=now + timedelta(minutes=20))
            ] == runs

def test_as_rows():
    pipeline = Pipeline([passing_stage, failing_stage, passing_stage], trigger="commits")
    runs = pipeline.simulation(now, [commit1], timedelta(minutes=60))
    rows = as_rows(pipeline, runs)
    assert ",".join(map(str,rows[0])) == "start_time,changes_included,Build,Build,Build,end_time"



def test_triggers():
    assert ([commit1, commit2], [commit3]) == commits_in_next_run([commit1, commit2, commit3], now)
    assert ([commit1, commit2], []) == commits_in_next_run([commit1, commit2], now)
    assert ([commit3], []) == commits_in_next_run([commit3], now + timedelta(minutes=10))


def test_several_runs():
    commits = [commit1, commit2, commit3]
    stages = [passing_stage]
    pipeline = Pipeline(stages, trigger="commits")
    runs = pipeline.simulation(now, commits, timedelta(minutes=60))
    assert len(runs) == 2
    assert runs[1].start_time == now + passing_stage.duration
    assert runs[1].changes_included == [commit3]
    assert runs[1].stage_results == [StageStatus.ok]
    assert runs[1].end_time == now + passing_stage.duration + passing_stage.duration


def test_several_concurrent_runs():
    commits = [commit1, commit2, commit3]
    stages = [passing_stage, passing_stage]
    pipeline = Pipeline(stages, trigger="commits")
    runs = pipeline.simulation(now, commits, timedelta(minutes=60))
    assert len(runs) == 2
    assert runs[1].start_time == now + passing_stage.duration
    assert runs[1].changes_included == [commit3]
    assert runs[1].stage_results == [StageStatus.ok, StageStatus.ok]
    assert runs[1].end_time == now + passing_stage.duration + passing_stage.duration + passing_stage.duration
