import pytest
from mlfq import MFLQScheduler, View, Controller, RoundRobinAlgorithm, FCFSAlgorithm, SJFAlgorithm, Process

@pytest.fixture(autouse=True)
def get_controller() -> Controller:
    scheduler: MFLQScheduler = \
        MFLQScheduler(
            priority_queues = [
                RoundRobinAlgorithm(),
                FCFSAlgorithm(),
                SJFAlgorithm()
            ],
            cpu = Process.default()
    )
    view: View = View(scheduler)
    controller: Controller = Controller(view, scheduler)
    return controller