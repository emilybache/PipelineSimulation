from datetime import datetime

from dataclasses import dataclass, field

from deploy import DeployPolicy, Deployer
from stages import StageStatus


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
    deployer: Deployer = Deployer(deploy_policy=DeployPolicy.NoDeploys)
    runs: list = field(default_factory=list)

    def simulation(self, start_time, commits, duration):
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
                              deploy_time=self.simulate_deploy(stage_results[-1]),
                              )
            now = now + self.stages[0].duration
            if future_commits and now < future_commits[0].time:
                now = future_commits[0].time

            self.runs.append(run)

        return self.runs

    def simulate_deploy(self, last_stage_result):
        if last_stage_result.status == StageStatus.ok:
            return str(self.deployer.deploy(last_stage_result.end_time))
        else:
            return ""


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

