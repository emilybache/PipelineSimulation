from datetime import timedelta

from export import as_rows

from pipeline import Pipeline

from test_pipeline import passing_stage, failing_stage, second_passing_stage, now, commit1


def test_as_rows(passing_stage, failing_stage, second_passing_stage):
    stages = [passing_stage, failing_stage, second_passing_stage]
    pipeline = Pipeline(stages, trigger="commits")
    runs = pipeline.simulation(now, [commit1], timedelta(minutes=60))
    rows = as_rows(stages, runs)
    assert ",".join(map(str,rows[0])) == "Start Time,Changes Included,Build,Build,AcceptanceTest,End Time,Deploy Time"
    assert ",".join(map(str,rows[1])) == "2018-04-03 08:00:00,['#001'],ok,fail,skip (previous failure),2018-04-03 08:20:00,"
