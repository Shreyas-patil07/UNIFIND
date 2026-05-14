"""
Audit logging system for UNIFIND backend.

Tracks critical security and business events:
- Authentication and authorization events
- Transaction lifecycle events
- Moderation actions
- Administrative actions
- Critical state changes
"""

import logging
from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional

from app.core.observability import ObservabilityContext, metrics

logger = logging.getLogger(__name__)


class AuditEventType(str, Enum):
    """Types of auditable events."""

    # Authentication Events
    AUTH_LOGIN_SUCCESS = "auth.login.success"
    AUTH_LOGIN_FAILURE = "auth.login.failure"
    AUTH_LOGOUT = "auth.logout"
    AUTH_TOKEN_REFRESH = "auth.token.refresh"
    AUTH_PASSWORD_RESET = "auth.password.reset"
    AUTH_EMAIL_VERIFICATION_SENT = "auth.email_verification.sent"
    AUTH_EMAIL_VERIFICATION_SUCCESS = "auth.email_verification.success"
    AUTH_EMAIL_VERIFICATION_FAILURE = "auth.email_verification.failure"

    # Authorization Events
    AUTHZ_ACCESS_GRANTED = "authz.access.granted"
    AUTHZ_ACCESS_DENIED = "authz.access.denied"
    AUTHZ_PERMISSION_CHANGED = "authz.permission.changed"

    # User Events
    USER_CREATED = "user.created"
    USER_UPDATED = "user.updated"
    USER_DELETED = "user.deleted"
    USER_PROFILE_VIEWED = "user.profile.viewed"
    USER_SUSPENDED = "user.suspended"
    USER_REACTIVATED = "user.reactivated"

    # Product Events
    PRODUCT_CREATED = "product.created"
    PRODUCT_UPDATED = "product.updated"
    PRODUCT_DELETED = "product.deleted"
    PRODUCT_PUBLISHED = "product.published"
    PRODUCT_UNPUBLISHED = "product.unpublished"
    PRODUCT_SOLD = "product.sold"

    # Transaction Events
    TRANSACTION_INITIATED = "transaction.initiated"
    TRANSACTION_COMPLETED = "transaction.completed"
    TRANSACTION_CANCELLED = "transaction.cancelled"
    TRANSACTION_REFUNDED = "transaction.refunded"
    TRANSACTION_DISPUTED = "transaction.disputed"

    # Moderation Events
    MODERATION_CONTENT_FLAGGED = "moderation.content.flagged"
    MODERATION_CONTENT_APPROVED = "moderation.content.approved"
    MODERATION_CONTENT_REJECTED = "moderation.content.rejected"
    MODERATION_USER_WARNED = "moderation.user.warned"
    MODERATION_USER_BANNED = "moderation.user.banned"
    MODERATION_REVIEW_DELETED = "moderation.review.deleted"

    # Admin Events
    ADMIN_CONFIG_CHANGED = "admin.config.changed"
    ADMIN_USER_IMPERSONATION = "admin.user.impersonation"
    ADMIN_DATA_EXPORT = "admin.data.export"
    ADMIN_BULK_OPERATION = "admin.bulk.operation"

    # Chat Events
    CHAT_MESSAGE_SENT = "chat.message.sent"
    CHAT_MESSAGE_DELETED = "chat.message.deleted"
    CHAT_CONVERSATION_STARTED = "chat.conversation.started"
    CHAT_USER_BLOCKED = "chat.user.blocked"

    # Review Events
    REVIEW_CREATED = "review.created"
    REVIEW_UPDATED = "review.updated"
    REVIEW_DELETED = "review.deleted"

    # Need Board Events
    NEED_CREATED = "need.created"
    NEED_UPDATED = "need.updated"
    NEED_DELETED = "need.deleted"
    NEED_FULFILLED = "need.fulfilled"


class AuditSeverity(str, Enum):
    """Severity levels for audit events."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AuditLogger:
    """
    Centralized audit logging system.

    Provides structured, tamper-evident logging of security and business events.
    """

    def __init__(self):
        self._logger = logging.getLogger(f"{__name__}.audit")
        self._event_count = 0

    def log_event(
        self,
        event_type: AuditEventType,
        severity: AuditSeverity = AuditSeverity.MEDIUM,
        actor_id: Optional[str] = None,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        action: Optional[str] = None,
        status: str = "success",
        details: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> None:
        """
        Log an audit event.

        Args:
            event_type: Type of event being logged
            severity: Severity level of the event
            actor_id: ID of the user/system performing the action
            resource_type: Type of resource being acted upon
            resource_id: ID of the resource
            action: Specific action performed
            status: Status of the action (success, failure, pending)
            details: Additional event details
            ip_address: IP address of the actor
            user_agent: User agent string
        """
        self._event_count += 1

        # Build audit record
        audit_record = {
            "event_id": self._event_count,
            "event_type": event_type.value,
            "severity": severity.value,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "actor_id": actor_id or ObservabilityContext.get_user_id() or "system",
            "resource_type": resource_type,
            "resource_id": resource_id,
            "action": action or event_type.value.split(".")[-1],
            "status": status,
            "ip_address": ip_address,
            "user_agent": user_agent,
            "details": details or {},
            **ObservabilityContext.get_context(),
        }

        # Determine log level based on severity
        log_level = self._get_log_level(severity)

        # Log the audit event
        self._logger.log(
            log_level,
            f"AUDIT: {event_type.value} - {action or 'action'} by {audit_record['actor_id']} "
            f"on {resource_type or 'resource'} [{status}]",
            extra={"extra_data": audit_record},
        )

        # Record metric
        metrics.increment(
            "audit.events.total",
            tags={"event_type": event_type.value, "severity": severity.value, "status": status},
        )

        # Alert on critical events
        if severity == AuditSeverity.CRITICAL:
            self._alert_critical_event(audit_record)

    def log_auth_event(
        self,
        event_type: AuditEventType,
        user_id: Optional[str] = None,
        email: Optional[str] = None,
        status: str = "success",
        reason: Optional[str] = None,
        ip_address: Optional[str] = None,
    ) -> None:
        """
        Log an authentication event.

        Args:
            event_type: Type of auth event
            user_id: User ID
            email: User email
            status: Status of the auth attempt
            reason: Reason for failure (if applicable)
            ip_address: IP address of the request
        """
        severity = AuditSeverity.HIGH if status == "failure" else AuditSeverity.MEDIUM

        self.log_event(
            event_type=event_type,
            severity=severity,
            actor_id=user_id,
            resource_type="user",
            resource_id=user_id,
            status=status,
            details={"email": email, "reason": reason},
            ip_address=ip_address,
        )

    def log_transaction_event(
        self,
        event_type: AuditEventType,
        transaction_id: str,
        buyer_id: str,
        seller_id: str,
        product_id: str,
        amount: Optional[float] = None,
        status: str = "success",
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Log a transaction event.

        Args:
            event_type: Type of transaction event
            transaction_id: Transaction ID
            buyer_id: Buyer user ID
            seller_id: Seller user ID
            product_id: Product ID
            amount: Transaction amount
            status: Transaction status
            details: Additional details
        """
        self.log_event(
            event_type=event_type,
            severity=AuditSeverity.HIGH,
            actor_id=buyer_id,
            resource_type="transaction",
            resource_id=transaction_id,
            status=status,
            details={
                "buyer_id": buyer_id,
                "seller_id": seller_id,
                "product_id": product_id,
                "amount": amount,
                **(details or {}),
            },
        )

    def log_moderation_event(
        self,
        event_type: AuditEventType,
        moderator_id: str,
        target_user_id: Optional[str] = None,
        target_resource_type: Optional[str] = None,
        target_resource_id: Optional[str] = None,
        reason: str = "",
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Log a moderation event.

        Args:
            event_type: Type of moderation event
            moderator_id: ID of the moderator
            target_user_id: ID of the user being moderated
            target_resource_type: Type of resource being moderated
            target_resource_id: ID of the resource
            reason: Reason for moderation action
            details: Additional details
        """
        self.log_event(
            event_type=event_type,
            severity=AuditSeverity.HIGH,
            actor_id=moderator_id,
            resource_type=target_resource_type or "user",
            resource_id=target_resource_id or target_user_id,
            status="success",
            details={"target_user_id": target_user_id, "reason": reason, **(details or {})},
        )

    def log_admin_event(
        self,
        event_type: AuditEventType,
        admin_id: str,
        action: str,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Log an administrative event.

        Args:
            event_type: Type of admin event
            admin_id: ID of the admin
            action: Action performed
            resource_type: Type of resource
            resource_id: ID of the resource
            details: Additional details
        """
        self.log_event(
            event_type=event_type,
            severity=AuditSeverity.CRITICAL,
            actor_id=admin_id,
            resource_type=resource_type,
            resource_id=resource_id,
            action=action,
            status="success",
            details=details,
        )

    def _get_log_level(self, severity: AuditSeverity) -> int:
        """Get logging level based on severity."""
        severity_map = {
            AuditSeverity.LOW: logging.INFO,
            AuditSeverity.MEDIUM: logging.INFO,
            AuditSeverity.HIGH: logging.WARNING,
            AuditSeverity.CRITICAL: logging.ERROR,
        }
        return severity_map.get(severity, logging.INFO)

    def _alert_critical_event(self, audit_record: Dict[str, Any]) -> None:
        """
        Alert on critical audit events.
        In production, this would trigger alerts via PagerDuty, Slack, etc.
        """
        self._logger.critical(
            f"CRITICAL AUDIT EVENT: {audit_record['event_type']} by {audit_record['actor_id']}",
            extra={"extra_data": audit_record},
        )


# Global audit logger instance
audit_logger = AuditLogger()


def audit_event(
    event_type: AuditEventType, severity: AuditSeverity = AuditSeverity.MEDIUM, **kwargs
):
    """
    Convenience function for logging audit events.

    Example:
        audit_event(
            AuditEventType.USER_CREATED,
            severity=AuditSeverity.MEDIUM,
            actor_id=current_user_id,
            resource_id=new_user_id,
            details={"email": user_email}
        )
    """
    audit_logger.log_event(event_type, severity, **kwargs)
