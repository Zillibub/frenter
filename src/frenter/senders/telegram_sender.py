import requests
from frenter.senders.base_sender import BaseSender


class TelegramSender(BaseSender):
    """
    Hardcoded sender for telegram bot
    Ideally it should have a full functionality but I took a few shortcuts here
    """

    def __init__(
            self,
            bot_token,
            chat_id,
    ):
        """

        :param bot_token:
        :param chat_id: can be retrieved by sending a message to the bot and reading it by request

        """
        self._bot_token = bot_token
        self._chat_id = chat_id
        self._base_url = "https://api.telegram.org"

    def _send(self, message: str):
        response = requests.post(
            f"{self._base_url}/bot{self._bot_token}/sendMessage", json={'chat_id': self._chat_id, 'text': message}
        )
        if response.status_code != 200:
            raise ValueError(f"Status code {response.status_code} on telegram bot sending: {response.content}")
