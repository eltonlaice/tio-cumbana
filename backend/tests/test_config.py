from app.config import Settings


def test_defaults():
    s = Settings(_env_file=None)
    assert s.claude_model == "claude-opus-4-7"
    assert s.use_managed_agent is False
    assert s.managed_agent_id == ""


def test_overrides_via_constructor():
    s = Settings(
        _env_file=None,
        anthropic_api_key="sk-test",
        claude_model="claude-opus-4-7",
        use_managed_agent=True,
        managed_agent_id="ag_xyz",
        managed_environment_id="env_xyz",
    )
    assert s.anthropic_api_key == "sk-test"
    assert s.use_managed_agent is True
    assert s.managed_agent_id == "ag_xyz"
