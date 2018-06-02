
from stages import StageStatus, StageRun
from test_pipeline import passing_stage, failing_stage, now


def test_stage_status_strings():
    assert str(StageStatus.ok) == "ok"
    assert ["ok", "fail", "foobar"] == list(map(str, [StageStatus.ok, StageStatus.fail, "foobar"]))


def test_stage_result(passing_stage, failing_stage):
    assert passing_stage.add_result(now, now) == StageRun(StageStatus.ok, now, now+passing_stage.duration)
    assert failing_stage.add_result(now, now) == StageRun(StageStatus.fail, now, now+failing_stage.duration)
