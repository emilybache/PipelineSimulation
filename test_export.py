from datetime import timedelta

from export import as_rows

from pipeline import Pipeline

from test_pipeline import passing_stage, failing_stage, second_passing_stage, now, commit1

def test_as_rows(passing_stage, failing_stage, second_passing_stage):
    pipeline = Pipeline([passing_stage, failing_stage, second_passing_stage], trigger="commits")
    runs = pipeline.simulation(now, [commit1], timedelta(minutes=60))
    rows = as_rows(pipeline, runs)
    assert ",".join(map(str,rows[0])) == "start_time,changes_included,Build,Build,AcceptanceTest,end_time"
