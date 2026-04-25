from app.prompts.tio_cumbana import build_system_prompt


def test_default_prompt_contains_persona_anchors():
    prompt = build_system_prompt()
    assert "Tio Cumbana" in prompt
    assert "Maluana" in prompt
    assert "Changana" in prompt
    assert "AQI Machava" in prompt


def test_custom_few_shot_is_injected():
    custom = "[exemplo personalizado]"
    prompt = build_system_prompt(few_shot=custom)
    assert custom in prompt
    assert "PLACEHOLDER" not in prompt


def test_default_few_shot_placeholder_present():
    prompt = build_system_prompt()
    assert "PLACEHOLDER" in prompt
