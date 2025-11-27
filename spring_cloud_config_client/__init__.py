import os
import sys

import requests
from requests.auth import HTTPBasicAuth

_config_server_url = os.getenv("CONFIG_SERVER_FQDN", "http://{host}:{port}/".format(host=os.getenv("CONFIG_SERVER_HOST", "localhost"),
                                                    port=os.getenv("CONFIG_SERVER_PORT", "8080")))
_fail_fast = os.getenv("CONFIG_CLIENT_FAIL_FAST", "False").lower() in ("true", "1", "t")
_retry_initial_interval = int(os.getenv("CONFIG_CLIENT_RETRY_INITIAL_INTERVAL", "1"))
_retry_max_interval = int(os.getenv("CONFIG_CLIENT_RETRY_MAX_INTERVAL", "10"))
_retry_max_attempts = int(os.getenv("CONFIG_CLIENT_RETRY_MAX_ATTEMPTS", "5"))
_retry_multiplier = float(os.getenv("CONFIG_CLIENT_RETRY_MULTIPLIER", "1.1"))


def _test():
    if _fail_fast:
        r = requests.get("{url}{test_profile}".format(url=_config_server_url, test_profile="application-kafka.yml"),
                         auth=HTTPBasicAuth(os.getenv("CONFIG_SERVER_USERNAME", "user"),
                                            os.getenv("CONFIG_SERVER_PASSWORD")))
        if r.status_code != 200:
            sys.exit(1)


if __name__ == "__main__":
    _test()
