from app.main import app, healthcheck, readiness_check


def test_healthcheck_reports_ok():
    assert healthcheck() == {"status": "ok"}


def test_readiness_check_reaches_database():
    assert readiness_check() == {"status": "ready"}


def test_system_routes_are_registered():
    paths = {route.path for route in app.routes if hasattr(route, "path")}
    assert "/api/health" in paths
    assert "/api/ready" in paths
