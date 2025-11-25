import importlib

import pytest


@pytest.fixture
def configured_props(monkeypatch):
    monkeypatch.delenv("CONFIG_SERVICE_FQDN", raising=False)
    monkeypatch.setenv("CONFIG_SERVICE_HOST", "localhost")
    monkeypatch.setenv("CONFIG_SERVICE_PORT", "8888")
    monkeypatch.setenv("CONFIG_USERNAME", "config")
    monkeypatch.setenv("CONFIG_PASSWORD", "config")
    monkeypatch.setenv("CONFIG_SERVICE_FAIL_FAST", "False")

    import spring_cloud_config_client # noqa: PLC0415
    from spring_cloud_config_client import props # noqa: PLC0415

    importlib.reload(spring_cloud_config_client)
    importlib.reload(props)
    return props


def test_reads_properties_from_real_config_server(configured_props):
    configured_props.init(profiles=["prod"])

    assert configured_props.get("spring.datasource.url") == "jdbc:postgresql://inventory-db:5432/inventory"
    assert configured_props.get("spring.datasource.username") == "inventory_app"
    assert configured_props.get("spring.kafka.topic.orders") == "inventory.orders"
    assert configured_props.get("spring.kafka.bootstrap-servers") == "broker1:9092,broker2:9092"
    logging_levels = configured_props.get("logging.level")
    assert isinstance(logging_levels, dict)
    assert configured_props.get("logging.level.root") == "INFO"
    assert configured_props.get("logging.level.com.example.inventory") == "DEBUG"
    assert configured_props.get("management.endpoints.web.exposure.include") == "health,info,prometheus"
