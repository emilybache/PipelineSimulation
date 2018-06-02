from datetime import timedelta, datetime

from deploy import Deployer, DeployPolicy

# this is a friday
now = datetime(year=2018,month=6,day=1,hour=9)


def test_every_passing():
    deploy_delay = timedelta(minutes=1)
    deployer = Deployer(deploy_delay=deploy_delay, deploy_policy=DeployPolicy.EveryPassing)
    assert deployer.deploy(now) == now + deploy_delay


def test_once_per_day():
    deploy_delay = timedelta(minutes=1)
    deployer = Deployer(deploy_delay=deploy_delay, deploy_policy=DeployPolicy.OnceADay, deploy_hour=9)
    assert deployer.deploy(now) == (datetime(year=2018, month=6, day=4, hour=9) + deploy_delay)
    # following the weekend


def test_once_per_week():
    deploy_delay = timedelta(minutes=1)
    deployer = Deployer(deploy_delay=deploy_delay,
                        deploy_policy=DeployPolicy.OnceAWeek,
                        deploy_hour=9,
                        deploy_day=3)
    assert deployer.deploy(now) == (datetime(year=2018, month=6, day=6, hour=9) + deploy_delay)
    # following wednesday
