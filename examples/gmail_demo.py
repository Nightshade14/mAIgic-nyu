"""Demo script showcasing Gmail API wrapper usage."""

import logging
from datetime import datetime, timedelta

from maigic_nyu.gmail.api import Gmail, GMailMessage

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def main() -> None:
    """Run Gmail API demo."""
    try:
        gmail = Gmail()
    except FileNotFoundError:
        logger.exception("Credentials file not found. Please check your configuration.")
        return
    except ValueError:
        logger.exception("Authentication failed: %s")
        return

    end_date = datetime.now()  # noqa: DTZ005
    start_date = end_date - timedelta(days=7)

    logger.info(
        "Fetching emails between %s and %s",
        start_date.strftime("%Y-%m-%d"),
        end_date.strftime("%Y-%m-%d"),
    )

    message_count = 0
    for message in gmail.query(
        start_date=start_date,
        end_date=end_date,
        max_results=10,
    ):
        message_count += 1
        full_message = gmail.get_message(message["id"])
        email = GMailMessage(full_message)

        logger.info("-" * 50)
        logger.info("Message #%d:", message_count)
        logger.info("Labels: %s", ", ".join(email.label_ids))
        logger.info("Thread ID: %s", email.thread_id)

        for part in email.parts:
            for header in part.headers:
                logger.info("%s: %s", header.name, header.value)

            if part.body:
                logger.info("Body snippet: %s", part.body[:100] + "..." if len(part.body) > 100 else part.body)  # noqa: E501, PLR2004

    logger.info("-" * 50)
    logger.info("Total messages processed: %d", message_count)


if __name__ == "__main__":
    main()
