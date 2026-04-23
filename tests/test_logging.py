import logging

from src.systems.log_system import configure_logging


def test_logging_configuration_allows_regular_logging() -> None:
    configure_logging()
    logger = logging.getLogger("test")
    logger.info("hello")
    assert logger.isEnabledFor(logging.INFO)
