"""Main entry point"""

import sys

if sys.argv[0].endswith("__main__.py"):
    sys.argv[0] = "python -m spring_cloud_config_client"
from . import _test as main

main()
