"""Allow running the CLI as `python -m evalmoraal`."""

import sys

from .cli import main

sys.exit(main())
