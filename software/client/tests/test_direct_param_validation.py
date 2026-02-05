from dbay import DBayClient

def test_missing_direct_params_raises():
    try:
        DBayClient(mode="direct")  # neither connection nor host/port provided
    except ValueError as e:
        assert "direct_host" in str(e) or "serial_port" in str(e)
    else:
        raise AssertionError("Expected ValueError for missing direct params")