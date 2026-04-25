from server import _mildew_risk


def test_mildew_risk_when_humid_overnight_in_temp_window():
    hourly = {
        "relative_humidity_2m": [60, 70, 88, 90, 92, 91, 80, 65],
        "temperature_2m":       [22, 20, 18, 17, 16, 17, 19, 24],
    }
    assert _mildew_risk(hourly) is True


def test_no_risk_when_humidity_too_low():
    hourly = {
        "relative_humidity_2m": [60, 65, 70, 75, 80, 78, 70, 65],
        "temperature_2m":       [20, 19, 18, 17, 17, 18, 19, 20],
    }
    assert _mildew_risk(hourly) is False


def test_no_risk_when_temperature_outside_window():
    hourly = {
        "relative_humidity_2m": [88, 90, 92, 91],
        "temperature_2m":       [28, 27, 26, 25],
    }
    assert _mildew_risk(hourly) is False


def test_handles_missing_keys():
    assert _mildew_risk({}) is False
    assert _mildew_risk({"relative_humidity_2m": []}) is False
