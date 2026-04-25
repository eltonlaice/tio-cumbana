from app.services.managed_agent import TioCumbanaManagedAgent, VigilanceDecision


def test_parse_no_action():
    raw = '{"action": "no_action", "reason": "humidity already dropped"}'
    decision = TioCumbanaManagedAgent._parse_decision(raw)
    assert decision.action == "no_action"
    assert decision.content is None
    assert "humidity" in (decision.reason or "")


def test_parse_message():
    raw = '{"action": "message", "content": "Dona Maria, vai chover"}'
    decision = TioCumbanaManagedAgent._parse_decision(raw)
    assert decision.action == "message"
    assert decision.content == "Dona Maria, vai chover"


def test_parse_invalid_json_returns_safe_no_action():
    decision = TioCumbanaManagedAgent._parse_decision("not json at all")
    assert decision.action == "no_action"
    assert decision.reason == "parse_error"


def test_parse_decision_returns_dataclass():
    decision = TioCumbanaManagedAgent._parse_decision('{"action":"no_action"}')
    assert isinstance(decision, VigilanceDecision)
