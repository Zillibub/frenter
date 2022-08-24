from time import sleep
from frenter.evaluator.evaluator import Evaluator
from frenter.senders.base_sender import BaseSender


class Loop:
    """
    Main loop for this application
    """

    def __init__(
            self,
            evaluator: Evaluator,
            sender: BaseSender,
            timeout: float,
    ):
        """

        :param evaluator:
        :param sender:
        :param timeout:
        """
        self.evaluator = evaluator
        self.sender = sender
        self.timeout = timeout

    def _inner(self):
        listing_reports = self.evaluator.step()

        for listing_report in listing_reports:
            self.sender.send(listing_report)

    def run(self):
        while True:
            self._inner()
            sleep(self.timeout)
