"""Base service layer helpers."""

from typing import Generic, TypeVar

RepositoryType = TypeVar("RepositoryType")


class BaseService(Generic[RepositoryType]):
    """Simple base class for application services."""

    def __init__(self, repository: RepositoryType):
        self.repository = repository
