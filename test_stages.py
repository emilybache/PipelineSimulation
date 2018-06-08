
from stages import StageStatus, StageRun
from test_pipeline import passing_stage, failing_stage, now


def test_stage_status_strings():
    assert str(StageStatus.ok) == "ok"
    assert ["ok", "fail", "foobar"] == list(map(str, [StageStatus.ok, StageStatus.fail, "foobar"]))
    assert str(StageRun(status=StageStatus.ok, start_time=now, end_time=now)) == "ok"


def test_stage_result(passing_stage, failing_stage):
    assert passing_stage.add_result(now, now) == StageRun(StageStatus.ok, now, now+passing_stage.duration)
    assert failing_stage.add_result(now, now) == StageRun(StageStatus.fail, now, now+failing_stage.duration)


def test_realistic_failure_recovery(passing_stage, failing_stage):
    end_of_first_stage_time = now+passing_stage.duration
    assert passing_stage.add_result(now, now) == StageRun(StageStatus.ok, now, end_of_first_stage_time)
    assert failing_stage.add_result(end_of_first_stage_time, now) == StageRun(StageStatus.fail, end_of_first_stage_time, end_of_first_stage_time+failing_stage.duration)
    start_of_next_pipeline = now + passing_stage.duration
    end_of_next_pipeline_first_stage = start_of_next_pipeline + passing_stage.duration
    assert passing_stage.add_result(start_of_next_pipeline, start_of_next_pipeline) == StageRun(StageStatus.ok, start_of_next_pipeline, end_of_next_pipeline_first_stage)
    assert failing_stage.add_result(end_of_next_pipeline_first_stage, start_of_next_pipeline) == StageRun(StageStatus.repeat_fail, end_of_next_pipeline_first_stage, end_of_next_pipeline_first_stage+failing_stage.duration)
