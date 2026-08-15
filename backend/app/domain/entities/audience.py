"""
Audience Domain Entities
Represents lists, tags and segments for organizing contacts.
"""
from datetime import datetime
from typing import Optional, List
from dataclasses import dataclass, field


@dataclass
class MailingList:
    """
    Domain entity representing a mailing list.
    
    Attributes:
        id: Unique identifier
        user_id: ID of the user who owns this list
        name: Display name of the list
        description: Description of the list's purpose
        contact_count: Number of contacts in list (denormalized for perf)
        is_active: Whether list is active
        created_at: When list was created
        updated_at: Last update timestamp
    """
    id: Optional[str] = None
    user_id: str = ""
    name: str = ""
    description: str = ""
    contact_count: int = 0
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class Tag:
    """
    Domain entity representing a contact tag for categorization.
    
    Attributes:
        id: Unique identifier
        user_id: ID of the user who owns this tag
        name: Tag name
        description: Tag description
        contact_count: Number of contacts with this tag (denormalized)
        created_at: When tag was created
    """
    id: Optional[str] = None
    user_id: str = ""
    name: str = ""
    description: str = ""
    contact_count: int = 0
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class Segment:
    """
    Domain entity representing a dynamic segment (filtered audience).
    
    Attributes:
        id: Unique identifier
        user_id: ID of the user who owns this segment
        name: Segment name
        description: Segment description
        filter_criteria: Dictionary defining segment filter logic
        contact_count: Estimated number of contacts matching criteria
        is_active: Whether segment is active
        created_at: When segment was created
        updated_at: Last update timestamp
    """
    id: Optional[str] = None
    user_id: str = ""
    name: str = ""
    description: str = ""
    filter_criteria: dict = field(default_factory=dict)
    contact_count: int = 0
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
