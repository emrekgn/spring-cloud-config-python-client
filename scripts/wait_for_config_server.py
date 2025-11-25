#!/usr/bin/env python3
from __future__ import annotations

import argparse
import time
from urllib.error import HTTPError, URLError
from urllib.request import urlopen


def wait(url: str, timeout: float, interval: float) -> None:
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            with urlopen(url, timeout=interval):
                return
        except (URLError, HTTPError, OSError):
            time.sleep(interval)
    raise SystemExit(f"Config server did not become healthy within {timeout} seconds")


def main() -> None:
    parser = argparse.ArgumentParser(description="Wait for the Spring Config server to be ready")
    parser.add_argument("--url", default="http://localhost:8888/actuator/health", help="Health check URL")
    parser.add_argument("--timeout", type=float, default=60.0, help="Max seconds to wait")
    parser.add_argument("--interval", type=float, default=2.0, help="Seconds between checks")
    args = parser.parse_args()
    wait(args.url, args.timeout, args.interval)


if __name__ == "__main__":
    main()
