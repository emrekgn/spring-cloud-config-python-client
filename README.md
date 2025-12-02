# spring-cloud-config-client

[![PyPI version](https://img.shields.io/pypi/v/spring-cloud-config-client.svg)](https://pypi.org/project/spring-cloud-config-client/)
![License](https://img.shields.io/github/license/emrekgn/spring-cloud-config-python-client)
![Build Status](https://github.com/emrekgn/spring-cloud-config-python-client/actions/workflows/python-package.yml/badge.svg)

A helper library written in Python to fetch configuration properties from [the Spring Cloud Config server](https://docs.spring.io/spring-cloud-config/reference/server.html).


## Development Setup

To contribute to this project, you’ll need to install some common prerequisites first, and then follow setup instructions.

### Prerequisites

* [uv](https://docs.astral.sh/uv/)
* make [for win](https://stackoverflow.com/a/32127632) (required on Windows, usually preinstalled on Linux/macOS)

### Setup

```shell
# Install Python 3.12 and all dependencies under ./venv locally
make install-dev
```

## How to Use

Fetch configuration the same way you would in a Spring Boot application. Below is a realistic client that pulls database, Kafka, and actuator settings exposed by a Spring Cloud Config Server:

```python
from spring_cloud_config_client import props

# Initialize with your Spring application name and active profiles
props.init("inventory-service", ["prod", "us-east-1"])

# Common Spring properties
db_url = props.get("spring.datasource.url")
db_user = props.get("spring.datasource.username")
db_password = props.get("spring.datasource.password")
connection_timeout = props.get(
    "spring.datasource.hikari.connection-timeout",
    default_value=30_000,
)

# Messaging and observability
kafka_servers = props.get("spring.kafka.bootstrap-servers")
order_topic = props.get("spring.kafka.topic.orders")
actuator_exposed = props.get(
    "management.endpoints.web.exposure.include",
    default_value="health,info,prometheus",
)

# You can also fetch structured sections
logging_levels = props.get("logging.level")
# {'root': 'INFO', 'com.example.inventory': 'DEBUG'}
```

The library can also make use of *environment variables*. So if your configuration property contains a placeholder (e.g. `${REDIS_HOST}` or `${KAFKA_HOST:localhost}` etc.) it will be replaced by its matching environment variable (`REDIS_HOST`, `KAFKA_HOST` etc.) if exists.\
If the environment variable cannot be found, it searches for an optional default value in the placeholder (e.g. `localhost` in `\${KAFKA_HOST:localhost}`) and if this is also not found, it throws an exception. Only alphanumeric characters and dash (`-`) are supported for default values.

## Environment Variables

Configure the client with these environment variables:

* **CONFIG_SERVER_FQDN** overrides host and port with a full URL (default `http://localhost:8080/`)
* **CONFIG_SERVER_HOST** host used when `CONFIG_SERVER_FQDN` is unset (default `localhost`)
* **CONFIG_SERVER_PORT** port paired with `CONFIG_SERVER_HOST` (default `8080`)
* **CONFIG_SERVER_USERNAME** HTTP basic auth username (default `user`)
* **CONFIG_SERVER_PASSWORD** HTTP basic auth password (default empty)
* **CONFIG_CLIENT_FAIL_FAST** exits when unable to reach the config server if set to `True` (default `False`)
* **CONFIG_CLIENT_RETRY_INITIAL_INTERVAL** wait (seconds) before the first retry (default `1`)
* **CONFIG_CLIENT_RETRY_MAX_INTERVAL** maximum wait (seconds) between retries (default `10`)
* **CONFIG_CLIENT_RETRY_MAX_ATTEMPTS** total attempts before giving up (default `5`)
* **CONFIG_CLIENT_RETRY_MULTIPLIER** exponential backoff multiplier applied between retries (default `1.1`)

## Unit Tests

```shell
make test
```

## Integration Tests

If you have Docker available, you can run a live integration test suite against an actual Spring Cloud Config Server:

```shell
make test-integration
```

The target spins up the server defined in `docker-compose.integration.yml`, serves the fixtures from `tests/integration/config-repo`, runs the tests in `tests/integration`, and tears everything down when finished.

## Versioning

We use semantic versioning. You can check [here](https://semver.org/) when and how to bump up the version.

```shell
make set-version VERSION=<NEW_VERSION>`
```
