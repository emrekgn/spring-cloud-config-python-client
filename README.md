# spring-cloud-config-client

A helper library written in Python to fetch configuration properties from [the Spring Cloud Config server](https://docs.spring.io/spring-cloud-config/reference/server.html).
There is still much to do, this lib is used only to abstract away some config-service related details from the Python services.

## How to Initialize
This project uses [uv](https://docs.astral.sh/uv/) for dependency management. After installing `uv`, run the sync command to create a local virtualenv with the locked dependencies.

```shell
uv sync
```

Use `uv run <command>` to execute scripts inside that environment.

## How to Release

Release process means the library passed all its tests & ready to be deployed on both PyPi and Maven registries. We use [semantic versioning](https://semver.org/) for each release so keep that in mind while setting a new version.

```shell
make release AUTH_TOKEN=<GITLAB_AUTH_TOKEN> VERSION=<NEW_VERSION>
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

The library can be configured via these environment variables:

* **CONFIG_SERVICE_HOST** default value: localhost
* **CONFIG_SERVICE_PORT** default value: 20000
* **CONFIG_SERVICE_FAIL_FAST** default value: False. If set to True, the library will sys.exits if it cannot connect to the config-service on startup or if it cannot connect to it during runtime after a max retry attempts.
* **CONFIG_SERVICE_RETRY_INITIAL_INTERVAL** default value: 1 (in seconds)
* **CONFIG_SERVICE_RETRY_MAX_INTERVAL** default value: 20 (in seconds)
* **CONFIG_SERVICE_RETRY_MAX_ATTEMPTS** default value: 5
* **CONFIG_SERVICE_RETRY_MULTIPLIER** default value: 1.1

## Integration Tests

If you have Docker available, you can run a live integration test suite against an actual Spring Cloud Config Server:

```shell
make test-integration
```

The target spins up the server defined in `docker-compose.integration.yml`, serves the fixtures from `tests/integration/config-repo`, runs the tests in `tests/integration`, and tears everything down when finished.

## Versioning

We use semantic versioning. You can check [here](https://semver.org/) when and how to bump up the version.

1. In order to bump up, just run `make set-version VERSION=<NEW_VERSION>`. This will
   1. Update the version string in [VERSION](VERSION) file,
   2. Set package version located in `pyproject.toml`.

Please don't manually modify pyproject.toml.
