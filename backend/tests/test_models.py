from models import Digest, IntelItem


def test_intel_item_has_required_columns():
    assert hasattr(IntelItem, "competitor")
    assert hasattr(IntelItem, "signal_type")
    assert hasattr(IntelItem, "threat_level")
    assert hasattr(IntelItem, "summary")
    assert hasattr(IntelItem, "happyco_response")
    assert hasattr(IntelItem, "confidence")
    assert hasattr(IntelItem, "embedding")
    assert hasattr(IntelItem, "source_url")
    assert hasattr(IntelItem, "raw_content")


def test_digest_has_required_columns():
    assert hasattr(Digest, "week_of")
    assert hasattr(Digest, "content")
    assert hasattr(Digest, "sent_at")
    assert hasattr(Digest, "recipient")


def test_intel_item_table_name():
    assert IntelItem.__tablename__ == "intel_items"


def test_digest_table_name():
    assert Digest.__tablename__ == "digests"
