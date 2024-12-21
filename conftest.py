import pytest
from mlfq import MLFQScheduler, View, Controller, RoundRobinAlgorithm, FCFSAlgorithm, SJFAlgorithm, Process, Q1_QUANTUM

@pytest.fixture(autouse=True)
def get_controller() -> Controller:
    scheduler: MLFQScheduler = \
        MLFQScheduler(
            priority_queues = [
                RoundRobinAlgorithm(Q1_QUANTUM),
                FCFSAlgorithm(),
                SJFAlgorithm()
            ],
            cpu = Process.default()
    )
    view: View = View(scheduler)
    controller: Controller = Controller(view, scheduler)
    return controller