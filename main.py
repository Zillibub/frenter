from src.frenter.loop.loop import Loop
from src.frenter.core.settings import settings
from src.frenter.senders.telegram_sender import TelegramSender
from src.frenter.evaluator.evaluator import Evaluator


def main():
    loop = Loop(
        evaluator=Evaluator(
            filter_params={},
            state_path="data/state.json",
            postcode_dataset_path="data/london_postcodes-ons-postcodes-directory-feb22.csv",
            pages_amount=5
        ),
        sender=TelegramSender(
            bot_token=settings.TELEGRAM_BOT_TOKEN,
            chat_id=settings.TELEGRAM_CHAT_ID,
        ),
        timeout=settings.LOOP_TIMEOUT
    )

    loop.run()


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()
