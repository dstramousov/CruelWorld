import logging

from src.systems.log_system import configure_logging, get_overlay_handler


def test_logging_buffer_collects_records() -> None:
    configure_logging("DEBUG")
    logging.getLogger("test").info("hello")
    assert any("hello" in record for record in get_overlay_handler().records)
