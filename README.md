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

A basic example:

```
from spring_cloud_config_client import props
props.init("patient-service", ["be", "kafka"]) # Init by service_name and profiles

t1 = get("kafka.bootstrap-servers", default_value="http://localhost:9092") # You can optionally provide a default value if the prop is not found
t2 = get("kafka.topic.person-status")
t3 = get("spring.datasource.hikari.connection-timeout")
t4 = get("room-metadata.default-door-coordinates") # It also supports multi-dimensional array types
t5 = get("kafka.topic") # It can also return dict types if you want to fetch a sub-group of properties
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

## Versioning

We use semantic versioning. You can check [here](https://semver.org/) when and how to bump up the version.

1. In order to bump up, just run `make set-version VERSION=<NEW_VERSION>`. This will 
   1. Update the version string in [VERSION](VERSION) file,
   2. Set package version located in `pyproject.toml`.

Please don't manually modify pyproject.toml.
