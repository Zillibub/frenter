import requests
from frenter.senders.base_sender import BaseSender


class TelegramSender(BaseSender):

    def __init__(
            self,
            bot_token,
            chat_id,
    ):
        self._bot_token = bot_token
        self._chat_id = chat_id
        self._base_url = "https://api.telegram.org"

    def _send(self, message: str):
        response = requests.post(
            f"{self._base_url}/bot{self._bot_token}/sendMessage", json={'chat_id': self._chat_id, 'text': message}
        )
        if response.status_code != 200:
            raise ValueError(f"Status code {response.status_code} on telegram bot sending")
