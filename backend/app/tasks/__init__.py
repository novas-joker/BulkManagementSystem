"""Celery background tasks."""

# Import all task modules to register them with Celery
from . import campaigns  # noqa: F401
from . import events  # noqa: F401

__all__ = ["campaigns", "events"]
