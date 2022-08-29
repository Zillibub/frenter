import logging
from time import sleep
from frenter.evaluator.evaluator import Evaluator


class Loop:
    """
    Main loop for this application
    """

    def __init__(
            self,
            evaluator: Evaluator,
            timeout: float,
    ):
        """

        :param evaluator:
        :param timeout:
        """
        self.evaluator = evaluator
        self.timeout = timeout

    def _inner(self):
        """
        Retrieves listings reports from evaluator and feeds them to the sender
        :return:
        """
        self.evaluator.step()

    def run(self):
        while True:
            logging.info("Starting iteration")
            self._inner()
            sleep(self.timeout)
