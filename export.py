import csv


def as_rows(pipeline, runs):
    rows = []
    stages = [stage.name for stage in pipeline.stages]
    fieldnames = ["start_time",
                  "changes_included"] + stages + ["end_time"]
    rows.append(fieldnames)
    for run in runs:
        row = [run.start_time, [str(change) for change in run.changes_included]]
        for stage in run.stage_results:
            row.append(str(stage))
        row.append(run.end_time)
        rows.append(row)
    return rows


def to_csv(filename, pipeline, runs):
    with open(filename + ".csv", "w") as f:
        writer = csv.writer(f)
        for row in as_rows(pipeline, runs):
            writer.writerow(row)