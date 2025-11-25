import logging
import os
import re
import sys
import time
from functools import reduce
from typing import Any

import requests
import yaml
from requests.auth import HTTPBasicAuth
from requests.exceptions import RequestException

from spring_cloud_config_client import _config_server_url, _fail_fast, _retry_initial_interval, _retry_max_interval, \
    _retry_max_attempts, _retry_multiplier
from spring_cloud_config_client.exceptions import ConfigPlaceholderError

_props: dict[str, Any] = {}
_regex = re.compile("\${([\w]+):?([\w.:\/-]*)}")  # noqa: W605


def init(application="", profiles=None):
    """
    Fetches and populates configuration properties specified by the service_name and profiles parameters.
    At least one of these parameters should be provided.

    :param service_name: (optional) Name of the service. Specify this only when there are service-specific
    configuration properties on the config service.

    :param profiles: (optional) An array of profile names (e.g. kafka, redis, ml).
    """
    if not application and not profiles:
        raise ValueError("At least one parameter should be provided!")
    if profiles is None:
        profiles = []
    _application_name = "application" if not application else application + "-application"

    _profiles = ",".join(profiles)
    _profiles = ("-" + _profiles) if not application else ("," + _profiles)

    retry_count = 0
    while retry_count < _retry_max_attempts:
        try:
            response = requests.get(
                f"{_config_server_url}{_application_name}{_profiles}.yml?resolvePlaceholders=false",
                auth=HTTPBasicAuth(os.getenv("CONFIG_USERNAME", "user"),
                                   os.getenv("CONFIG_PASSWORD")),
                timeout=_retry_max_interval)
            if response.status_code == 200:
                logging.info("Fetched configuration properties successfully.")
                loaded_props = yaml.safe_load(response.text) or {}
                _props.clear()
                _props.update(loaded_props)
                break
            logging.error("Something went wrong while fetching configuration properties: %s",
                            response.reason)
            if _fail_fast:
                sys.exit(1)
        except RequestException:
            logging.exception("Error while requesting config service")
        retry_count += 1
        if retry_count < _retry_max_attempts:
            interval = _retry_initial_interval * (_retry_multiplier ** retry_count)
            logging.info("Retrying in %d seconds...", interval)
            time.sleep(interval)
    else:
        logging.error("Max retries reached. Could not fetch configuration properties.")
        if _fail_fast:
            sys.exit(1)


def get(property_name: str, default_value: Any = None):
    """
    Returns the property value specified by the property_name if it exists, otherwise returns the default_value.

    :param property_name: Property name (e.g. 'kafka.topic.room-status-msreader').
    :param default_value: (optional) Default value if the property does not exist (defaults to None).
    :return:
    """
    raw_value = reduce(lambda d, key: d.get(key, default_value) if isinstance(d, dict) else default_value,
                       property_name.split("."), _props)
    raw_value = _regex.sub(_resolve_placeholder, raw_value) if isinstance(raw_value, str) else raw_value
    property_key = property_name.replace(".", "_").replace("-", "_").upper()
    return os.environ.get(property_key, raw_value)


def _resolve_placeholder(match):
    env_var = match.group(1)
    opt_default_val = match.group(2)
    replacement = os.getenv(env_var, opt_default_val)
    if not replacement:
        logging.error("Cannot find an environment variable or a default value for placeholder: %s", env_var)
        raise ConfigPlaceholderError(
            f"Cannot find an environment variable or a default value for placeholder: {env_var}")
    return replacement
