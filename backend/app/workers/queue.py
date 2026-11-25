"""Task queue setup for running comment analysis in the background.

Holds the queue connection (Redis, `Config.REDIS_URL`) and queue configuration.
The queue library is not chosen yet: agree on it with the repo owner before
adding a package (see AGENTS.md).
"""

from app.core.config import Config

REDIS_URL = Config.REDIS_URL
