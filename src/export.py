import csv


def as_rows(stages, runs):
    rows = []
    stages = [stage.name for stage in stages]
    fieldnames = ["Start Time",
                  "Changes Included"] + stages + \
                 ["End Time", "Deploy Time"]
    rows.append(fieldnames)
    for run in runs:
        row = [run.start_time, [str(change) for change in run.changes_included]]
        for stage in run.stage_results:
            row.append(str(stage))
        row.append(run.end_time)
        if run.deploy_time:
            row.append(run.deploy_time)
        else:
            row.append("")
        rows.append(row)
    return rows


def to_csv(filename, stages, runs):
    with open(filename + ".csv", "w") as f:
        writer = csv.writer(f)
        for row in as_rows(stages, runs):
            writer.writerow(row)


def print_metrics(simulation_name, pipeline_metrics):
    with open(simulation_name + ".txt", "w") as f:
        f.write(pipeline_metrics.pretty_print())