from __future__ import annotations

import importlib
from types import SimpleNamespace

import pytest
from requests.auth import HTTPBasicAuth
from requests.exceptions import RequestException

from spring_cloud_config_client.exceptions import ConfigPlaceholderError


@pytest.fixture
def reload_props(monkeypatch):
    defaults = {
        "CONFIG_SERVER_HOST": "config-service",
        "CONFIG_SERVER_PORT": "8012",
        "CONFIG_CLIENT_FAIL_FAST": "False",
        "CONFIG_CLIENT_RETRY_INITIAL_INTERVAL": "1",
        "CONFIG_CLIENT_RETRY_MAX_INTERVAL": "15",
        "CONFIG_CLIENT_RETRY_MAX_ATTEMPTS": "3",
        "CONFIG_CLIENT_RETRY_MULTIPLIER": "2",
        "CONFIG_SERVER_USERNAME": "svc-user",
        "CONFIG_SERVER_PASSWORD": "s3cret",
        "CONFIG_USERNAME": "svc-user",
        "CONFIG_PASSWORD": "s3cret",
    }
    env_vars = [*defaults, "CONFIG_SERVER_FQDN"]

    def _reload(**extra_env):
        for var in env_vars:
            monkeypatch.delenv(var, raising=False)
        env = {**defaults, **extra_env}
        for key, value in env.items():
            if value is not None:
                monkeypatch.setenv(key, value)
        importlib.reload(importlib.import_module("spring_cloud_config_client"))
        return importlib.reload(importlib.import_module("spring_cloud_config_client.props"))

    return _reload


def _load_props_from_yaml(props, monkeypatch, yaml_content):
    def fake_get(*_, **__):
        return SimpleNamespace(status_code=200, text=yaml_content, reason="OK")

    monkeypatch.setattr(props.requests, "get", fake_get)
    props.init("inventory", ["test"])


def test_init_requires_application_or_profiles(reload_props):
    props = reload_props()

    with pytest.raises(ValueError):
        props.init()


def test_init_fetches_and_parses_remote_yaml(reload_props, monkeypatch):
    props = reload_props(CONFIG_CLIENT_RETRY_MAX_INTERVAL="25")
    captured = {}

    def fake_get(url, auth=None, timeout=None):
        captured["url"] = url
        captured["auth"] = auth
        captured["timeout"] = timeout
        body = (
            "simple: ok\n"
            "nested:\n"
            "  key: 42\n"
        )
        return SimpleNamespace(status_code=200, text=body, reason="OK")

    monkeypatch.setattr(props.requests, "get", fake_get)

    props.init("inventory", ["prod", "east"])

    assert captured["url"] == (
        "http://config-service:8012/"
        "inventory-application,prod,east.yml?resolvePlaceholders=false"
    )
    assert isinstance(captured["auth"], HTTPBasicAuth)
    assert captured["auth"].username == "svc-user"
    assert captured["auth"].password == "s3cret"
    assert captured["timeout"] == 25
    assert props.get("simple") == "ok"
    assert props.get("nested.key") == 42


def test_init_retries_until_success_without_fail_fast(reload_props, monkeypatch):
    props = reload_props(
        CONFIG_CLIENT_RETRY_MAX_ATTEMPTS="3",
        CONFIG_CLIENT_RETRY_INITIAL_INTERVAL="1",
        CONFIG_CLIENT_RETRY_MULTIPLIER="2",
    )
    attempts = {"count": 0}

    def flaky_get(*_, **__):
        attempts["count"] += 1
        if attempts["count"] < 3:
            raise RequestException("temporary failure")
        return SimpleNamespace(status_code=200, text="value: works", reason="OK")

    sleeps: list[int] = []
    monkeypatch.setattr(props.requests, "get", flaky_get)
    monkeypatch.setattr(props.time, "sleep", lambda seconds: sleeps.append(seconds))

    props.init("orders", ["prod"])

    assert attempts["count"] == 3
    assert sleeps == [2, 4]
    assert props.get("value") == "works"


def test_init_exits_immediately_when_fail_fast_is_enabled(reload_props, monkeypatch):
    props = reload_props(CONFIG_CLIENT_FAIL_FAST="True")

    def failing_get(*_, **__):
        return SimpleNamespace(status_code=503, text="", reason="Service Unavailable")

    monkeypatch.setattr(props.requests, "get", failing_get)

    with pytest.raises(SystemExit):
        props.init(application="billing")


def test_get_prefers_environment_override(reload_props, monkeypatch):
    props = reload_props()
    _load_props_from_yaml(
        props,
        monkeypatch,
        "service:\n  name-value: from-config\n",
    )
    monkeypatch.setenv("SERVICE_NAME_VALUE", "from-env")

    assert props.get("service.name-value") == "from-env"


def test_get_resolves_placeholders_with_defaults(reload_props, monkeypatch):
    props = reload_props()
    _load_props_from_yaml(
        props,
        monkeypatch,
        'service:\n  endpoint: "http://${SERVICE_HOST:localhost}:${SERVICE_PORT:8080}/health"\n',
    )
    monkeypatch.setenv("SERVICE_HOST", "api.internal")

    assert props.get("service.endpoint") == "http://api.internal:8080/health"


def test_get_raises_when_placeholder_missing_and_no_default(reload_props, monkeypatch):
    props = reload_props()
    _load_props_from_yaml(
        props,
        monkeypatch,
        "broken:\n  value: redis://${MISSING_HOST}\n",
    )

    with pytest.raises(ConfigPlaceholderError):
        props.get("broken.value")
