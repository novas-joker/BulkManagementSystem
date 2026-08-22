"""SQLAlchemy models for the MailForge application."""

import uuid
from datetime import datetime
from enum import Enum as PyEnum

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    JSON,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship

from app.core.database import Base


class UserRole(str, PyEnum):
    ADMIN = "admin"
    USER = "user"
    VIEWER = "viewer"


class UserStatus(str, PyEnum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"


class ContactStatus(str, PyEnum):
    SUBSCRIBED = "subscribed"
    UNSUBSCRIBED = "unsubscribed"
    BOUNCED = "bounced"
    COMPLAINED = "complained"


class ContactSource(str, PyEnum):
    MANUAL = "manual"
    IMPORT = "import"
    API = "api"
    SIGNUP_FORM = "signup_form"
    ZOHO_SYNC = "zoho_sync"


class TemplateType(str, PyEnum):
    STANDARD = "standard"
    PROMOTIONAL = "promotional"
    TRANSACTIONAL = "transactional"
    NEWSLETTER = "newsletter"


class CampaignStatus(str, PyEnum):
    DRAFT = "draft"
    SCHEDULED = "scheduled"
    QUEUED = "queued"
    SENDING = "sending"
    SENT = "sent"
    PAUSED = "paused"
    CANCELLED = "cancelled"
    FAILED = "failed"


class CampaignType(str, PyEnum):
    BULK = "bulk"
    TRANSACTIONAL = "transactional"
    AUTOMATION = "automation"
    NEWSLETTER = "newsletter"


class ProviderType(str, PyEnum):
    ZEPTOMAIL = "zeptomail"
    SMTP = "smtp"
    ZOHO_CAMPAIGNS = "zoho_campaigns"


class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String(255), unique=True, nullable=False, index=True)
    full_name = Column(String(255), nullable=False, default="")
    password_hash = Column(String(255), nullable=False)
    role = Column(String(20), default=UserRole.USER.value, nullable=False)
    status = Column(String(20), default=UserStatus.ACTIVE.value, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    last_login_at = Column(DateTime, nullable=True)
    subscriber_count_bracket = Column(String(40), nullable=True)
    previous_tool = Column(String(120), nullable=True)
    business_industry = Column(String(80), nullable=True)
    business_website = Column(String(500), nullable=True)
    compliance_address = Column(JSON, nullable=True)
    user_primary_goal = Column(String(80), nullable=True)
    product_updates_consent = Column(Boolean, nullable=True)
    onboarding_phase = Column(Integer, default=1, nullable=False)
    onboarding_completed = Column(Boolean, default=False, nullable=False)

    contacts = relationship("Contact", back_populates="user", cascade="all, delete-orphan")
    mailing_lists = relationship("MailingList", back_populates="user", cascade="all, delete-orphan")
    tags = relationship("Tag", back_populates="user", cascade="all, delete-orphan")
    segments = relationship("Segment", back_populates="user", cascade="all, delete-orphan")
    templates = relationship("EmailTemplate", back_populates="user", cascade="all, delete-orphan")
    campaigns = relationship("Campaign", back_populates="user", cascade="all, delete-orphan")
    refresh_tokens = relationship("RefreshToken", back_populates="user", cascade="all, delete-orphan")
    password_reset_tokens = relationship("PasswordResetToken", back_populates="user", cascade="all, delete-orphan")
    provider_credentials = relationship("ProviderCredential", back_populates="user", cascade="all, delete-orphan")
    suppressions = relationship("Suppression", back_populates="user", cascade="all, delete-orphan")
    integrations = relationship("Integration", back_populates="user", cascade="all, delete-orphan")


class Contact(Base):
    __tablename__ = "contacts"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    email = Column(String(255), nullable=False, index=True)
    first_name = Column(String(120), default="", nullable=False)
    last_name = Column(String(120), default="", nullable=False)
    status = Column(String(20), default=ContactStatus.SUBSCRIBED.value, nullable=False)
    source = Column(String(30), default=ContactSource.MANUAL.value, nullable=False)
    custom_fields = Column(JSON, default=dict, nullable=False)
    is_valid_email = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="contacts")
    list_memberships = relationship("ListContact", back_populates="contact", cascade="all, delete-orphan")
    contact_tags = relationship("ContactTag", back_populates="contact", cascade="all, delete-orphan")
    received_events = relationship("EmailEvent", back_populates="contact")
    campaign_recipients = relationship("CampaignRecipient", back_populates="contact")

    __table_args__ = (UniqueConstraint("user_id", "email", name="uq_contact_user_email"),)


class MailingList(Base):
    __tablename__ = "mailing_lists"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, default="", nullable=False)
    contact_count = Column(Integer, default=0, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="mailing_lists")
    memberships = relationship("ListContact", back_populates="mailing_list", cascade="all, delete-orphan")


class Tag(Base):
    __tablename__ = "tags"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(120), nullable=False)
    description = Column(Text, default="", nullable=False)
    contact_count = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="tags")
    contact_tags = relationship("ContactTag", back_populates="tag", cascade="all, delete-orphan")

    __table_args__ = (UniqueConstraint("user_id", "name", name="uq_tag_user_name"),)


class Segment(Base):
    __tablename__ = "segments"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, default="", nullable=False)
    filter_criteria = Column(JSON, default=dict, nullable=False)
    contact_count = Column(Integer, default=0, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="segments")

    __table_args__ = (UniqueConstraint("user_id", "name", name="uq_segment_user_name"),)


class EmailTemplate(Base):
    __tablename__ = "email_templates"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    subject = Column(String(255), nullable=False)
    html_content = Column(Text, default="", nullable=False)
    plain_text_content = Column(Text, default="", nullable=False)
    preview_text = Column(Text, default="", nullable=False)
    template_type = Column(String(30), default=TemplateType.STANDARD.value, nullable=False)
    template_variables = Column(JSON, default=list, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    usage_count = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="templates")
    campaigns = relationship("Campaign", back_populates="template")

    __table_args__ = (UniqueConstraint("user_id", "name", name="uq_template_user_name"),)


class Campaign(Base):
    __tablename__ = "campaigns"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    template_id = Column(String(36), ForeignKey("email_templates.id", ondelete="SET NULL"), nullable=True)
    name = Column(String(255), nullable=False)
    subject = Column(String(255), nullable=False)
    status = Column(String(30), default=CampaignStatus.DRAFT.value, nullable=False)
    campaign_type = Column(String(30), default=CampaignType.BULK.value, nullable=False)
    audience_criteria = Column(JSON, default=dict, nullable=False)
    scheduled_at = Column(DateTime, nullable=True)
    sent_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    total_recipients = Column(Integer, default=0, nullable=False)
    delivered_count = Column(Integer, default=0, nullable=False)
    opened_count = Column(Integer, default=0, nullable=False)
    clicked_count = Column(Integer, default=0, nullable=False)
    bounced_count = Column(Integer, default=0, nullable=False)
    failed_count = Column(Integer, default=0, nullable=False)
    is_test = Column(Boolean, default=False, nullable=False)

    user = relationship("User", back_populates="campaigns")
    template = relationship("EmailTemplate", back_populates="campaigns")
    recipients = relationship("CampaignRecipient", back_populates="campaign", cascade="all, delete-orphan")
    email_events = relationship("EmailEvent", back_populates="campaign")

    __table_args__ = (UniqueConstraint("user_id", "name", name="uq_campaign_user_name"),)


class CampaignRecipient(Base):
    __tablename__ = "campaign_recipients"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    campaign_id = Column(String(36), ForeignKey("campaigns.id", ondelete="CASCADE"), nullable=False, index=True)
    contact_id = Column(String(36), ForeignKey("contacts.id", ondelete="CASCADE"), nullable=False, index=True)
    email = Column(String(255), nullable=False)
    status = Column(String(30), default="pending", nullable=False)
    opened_at = Column(DateTime, nullable=True)
    clicked_at = Column(DateTime, nullable=True)
    delivered_at = Column(DateTime, nullable=True)
    bounced_at = Column(DateTime, nullable=True)
    failed_reason = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    campaign = relationship("Campaign", back_populates="recipients")
    contact = relationship("Contact", back_populates="campaign_recipients")

    __table_args__ = (UniqueConstraint("campaign_id", "contact_id", name="uq_campaign_recipient"),)


class EmailEvent(Base):
    __tablename__ = "email_events"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    campaign_id = Column(String(36), ForeignKey("campaigns.id", ondelete="CASCADE"), nullable=True, index=True)
    contact_id = Column(String(36), ForeignKey("contacts.id", ondelete="CASCADE"), nullable=True, index=True)
    email = Column(String(255), nullable=False)
    event_type = Column(String(40), default="sent", nullable=False)
    event_data = Column(JSON, default=dict, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    campaign = relationship("Campaign", back_populates="email_events")
    contact = relationship("Contact", back_populates="received_events")


class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    token = Column(Text, nullable=False, unique=True)
    expires_at = Column(DateTime, nullable=True)
    revoked = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="refresh_tokens")


class PasswordResetToken(Base):
    __tablename__ = "password_reset_tokens"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    token_hash = Column(String(64), nullable=False, unique=True, index=True)
    expires_at = Column(DateTime, nullable=False)
    used_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="password_reset_tokens")


class ProviderCredential(Base):
    __tablename__ = "provider_credentials"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    provider = Column(String(30), default=ProviderType.ZEPTOMAIL.value, nullable=False)
    credential_name = Column(String(255), nullable=False)
    encrypted_value = Column(Text, nullable=False)
    metadata_json = Column("metadata", JSON, default=dict, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="provider_credentials")


class Suppression(Base):
    __tablename__ = "suppressions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    email = Column(String(255), nullable=False, index=True)
    reason = Column(String(255), default="", nullable=False)
    source = Column(String(50), default="manual", nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="suppressions")

    __table_args__ = (UniqueConstraint("user_id", "email", name="uq_suppression_user_email"),)


class Integration(Base):
    __tablename__ = "integrations"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    provider = Column(String(30), default=ProviderType.ZOHO_CAMPAIGNS.value, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    config = Column(JSON, default=dict, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="integrations")

    __table_args__ = (UniqueConstraint("user_id", "name", name="uq_integration_user_name"),)


class ListContact(Base):
    __tablename__ = "list_contacts"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    list_id = Column(String(36), ForeignKey("mailing_lists.id", ondelete="CASCADE"), nullable=False, index=True)
    contact_id = Column(String(36), ForeignKey("contacts.id", ondelete="CASCADE"), nullable=False, index=True)
    added_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    mailing_list = relationship("MailingList", back_populates="memberships")
    contact = relationship("Contact", back_populates="list_memberships")

    __table_args__ = (UniqueConstraint("list_id", "contact_id", name="uq_list_contact"),)


class ContactTag(Base):
    __tablename__ = "contact_tags"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    contact_id = Column(String(36), ForeignKey("contacts.id", ondelete="CASCADE"), nullable=False, index=True)
    tag_id = Column(String(36), ForeignKey("tags.id", ondelete="CASCADE"), nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    contact = relationship("Contact", back_populates="contact_tags")
    tag = relationship("Tag", back_populates="contact_tags")

    __table_args__ = (UniqueConstraint("contact_id", "tag_id", name="uq_contact_tag"),)
