from src.components.statuses import StatusReceiverComponent


def test_status_receiver_defaults_empty() -> None:
    statuses = StatusReceiverComponent()
    assert statuses.active == {}
    assert statuses.names() == []
