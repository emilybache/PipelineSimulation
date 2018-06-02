
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from numpy.random import randint



@dataclass
class PipelineRun:
    start_time: datetime
    end_time: datetime
    changes_included: list = field(default_factory=list)
    stage_results: list = field(default_factory=list)
    deploy_time: datetime = None


@dataclass(eq=True)
class Pipeline:
    stages: list = field(default_factory=list)
    trigger: str = "commits"

    def simulation(self, start_time, commits, duration):
        result = []
        now = start_time
        future_commits = commits
        while future_commits \
                and (now < start_time + duration):
            commits_this_run, future_commits = commits_in_next_run(future_commits, now)
            stage_results = simulate_stage_results(self.stages, now)
            end_time = stage_results[-1].end_time

            run = PipelineRun(start_time=now,
                              end_time=end_time,
                              changes_included=commits_this_run,
                              stage_results=[result.status for result in stage_results],
                              )
            now = now + self.stages[0].duration
            if future_commits and now < future_commits[0].time:
                now = future_commits[0].time
            result.append(run)

        return result


def simulate_stage_results(stages, now):
    results = []
    previous_result = None
    run_start_time = now
    for stage in stages:
        result = stage.add_result(now, run_start_time, previous_result)
        results.append(result)
        previous_result = result
        now = previous_result.end_time
    return results


def commits_in_next_run(commits, now):
    commits_next_run, new_commits = [], []
    for commit in commits:
        (commits_next_run if commit.time <= now else new_commits).append(commit)
    return commits_next_run, new_commits

