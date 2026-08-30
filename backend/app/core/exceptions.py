from typing import Optional, Dict, Any
from fastapi import HTTPException, status


class RecoverAIException(Exception):
    def __init__(
        self,
        code: str,
        message: str,
        status_code: int = status.HTTP_400_BAD_REQUEST,
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message)
        self.code = code
        self.message = message
        self.status_code = status_code
        self.details = details or {}


class PolicyViolationException(RecoverAIException):
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            code="RECOVERY_POLICY_BLOCKED",
            message=message,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            details=details,
        )


class IdempotencyViolationException(RecoverAIException):
    def __init__(self, message: str = "Duplicate operation rejected.", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            code="IDEMPOTENCY_CONFLICT",
            message=message,
            status_code=status.HTTP_409_CONFLICT,
            details=details,
        )


class WebhookSignatureException(RecoverAIException):
    def __init__(self, message: str = "Invalid webhook signature."):
        super().__init__(
            code="INVALID_WEBHOOK_SIGNATURE",
            message=message,
            status_code=status.HTTP_400_BAD_REQUEST,
        )


class ResourceNotFoundException(RecoverAIException):
    def __init__(self, resource_type: str, resource_id: str):
        super().__init__(
            code="RESOURCE_NOT_FOUND",
            message=f"{resource_type} with ID '{resource_id}' was not found.",
            status_code=status.HTTP_404_NOT_FOUND,
        )


class UnauthorizedApprovalException(RecoverAIException):
    def __init__(self, message: str = "User not authorized to approve recovery action."):
        super().__init__(
            code="UNAUTHORIZED_APPROVAL",
            message=message,
            status_code=status.HTTP_403_FORBIDDEN,
        )


class ForbiddenException(RecoverAIException):
    def __init__(self, message: str = "Role not authorized to perform this operation."):
        super().__init__(
            code="FORBIDDEN_OPERATION",
            message=message,
            status_code=status.HTTP_403_FORBIDDEN,
        )
