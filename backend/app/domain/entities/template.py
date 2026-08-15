"""
Template Domain Entity
Represents reusable email templates.
"""
from datetime import datetime
from typing import Optional
from enum import Enum
from dataclasses import dataclass, field


class TemplateType(str, Enum):
    """Type of email template."""
    STANDARD = "standard"
    PROMOTIONAL = "promotional"
    TRANSACTIONAL = "transactional"
    NEWSLETTER = "newsletter"


@dataclass
class EmailTemplate:
    """
    Domain entity representing a reusable email template.
    
    Attributes:
        id: Unique identifier
        user_id: ID of the user who owns this template
        name: Template name
        subject: Email subject line
        html_content: Email body (HTML)
        plain_text_content: Email body (Plain text fallback)
        preview_text: Preview text shown in email clients
        template_type: Classification of template type
        template_variables: List of available template variables (e.g., {{first_name}})
        is_active: Whether template is active
        usage_count: Number of campaigns using this template (denormalized)
        created_at: When template was created
        updated_at: Last update timestamp
    """
    id: Optional[str] = None
    user_id: str = ""
    name: str = ""
    subject: str = ""
    html_content: str = ""
    plain_text_content: str = ""
    preview_text: str = ""
    template_type: TemplateType = TemplateType.STANDARD
    template_variables: list = field(default_factory=list)
    is_active: bool = True
    usage_count: int = 0
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    def has_required_fields(self) -> bool:
        """Validate that template has minimum required fields."""
        return bool(self.name and self.subject and self.html_content)

    def get_personalization_variables(self) -> list:
        """Extract personalization variables from template."""
        import re
        # Find all {{variable}} patterns
        return re.findall(r'\{\{(\w+)\}\}', self.html_content + self.subject)
