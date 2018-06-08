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
    deploy_time: str = ""

    def __str__(self):
        s = "Pipeline Run("
        s += str(self.start_time) + ", "
        s += str(self.end_time) + ", "
        s += str(self.changes_included) + ", "
        s += "[" + ''.join([str(run) for run in self.stage_results]) + "], "
        s += str(self.deploy_time)
        s += ")"
        return s


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
            stage_results = self.simulate_stage_results(now)
            end_time = stage_results[-1].end_time

            run = PipelineRun(start_time=now,
                              end_time=end_time,
                              changes_included=commits_this_run,
                              stage_results=stage_results,
                              )

            now = now + self.stages[0].duration
            if future_commits and now < future_commits[0].time:
                now = future_commits[0].time

            self.runs.append(run)

        self.deployer.add_deployments(self.runs)

        return self.runs

    def simulate_stage_results(self, now):
        results = []
        previous_result = None
        run_start_time = now
        for stage in self.stages:
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

