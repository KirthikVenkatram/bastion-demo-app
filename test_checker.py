from checker import HealthResult, print_report


def test_health_result_repr(capsys):
    results = [
        HealthResult(url="https://example.com", status_code=200, latency_ms=123.4),
        HealthResult(url="https://broken.example", status_code=None, latency_ms=None, error="timeout"),
    ]
    print_report(results)
    captured = capsys.readouterr()
    assert "example.com" in captured.out
    assert "broken.example" in captured.out
    assert "ERROR" in captured.out
