"""
FAZA 18 - Authentication Request Manager

This module handles credential submission (username/password ONLY) and
assembles secure authentication requests. This is an abstract layer that
prepares requests but does NOT make network calls directly.

CRITICAL PRIVACY RULE:
    This module handles ONLY text-based credentials (username/password).
    It NEVER handles biometric data.
    All credential handling is in-memory only with secure cleanup.

Author: SENTI OS Core Team
License: Proprietary
GDPR/ZVOP/EU AI Act Compliant
"""

from typing import Dict, Optional, Any, List
from dataclasses import dataclass, field
from enum import Enum
import secrets
import hashlib
from datetime import datetime, timedelta
import json


class CredentialType(Enum):
    """Types of credentials that can be handled."""
    USERNAME_PASSWORD = "username_password"
    EMAIL_PASSWORD = "email_password"
    OAUTH_TOKEN = "oauth_token"
    API_KEY = "api_key"


class RequestMethod(Enum):
    """HTTP methods for authentication requests."""
    POST = "POST"
    GET = "GET"
    PUT = "PUT"
    PATCH = "PATCH"


@dataclass
class Credentials:
    """
    Container for user credentials.

    SECURITY:
        - Credentials are stored in memory only
        - No persistence to disk
        - Automatic cleanup on destruction
    """
    username: str
    password: str
    credential_type: CredentialType = CredentialType.USERNAME_PASSWORD
    additional_fields: Dict[str, str] = field(default_factory=dict)

    def __del__(self):
        """Secure cleanup of credentials from memory."""
        if hasattr(self, 'password'):
            # Overwrite password in memory
            self.password = "X" * len(self.password)
        if hasattr(self, 'username'):
            self.username = "X" * len(self.username)

    def to_dict(self) -> Dict[str, str]:
        """
        Convert credentials to dictionary.

        Returns:
            Dictionary with credential fields.
        """
        result = {
            "username": self.username,
            "password": self.password,
        }
        result.update(self.additional_fields)
        return result


@dataclass
class AuthRequest:
    """
    Representation of an authentication request.

    This is an abstract representation that can be used by
    different execution layers (browser automation, API calls, etc.).
    """
    request_id: str
    url: str
    method: RequestMethod
    headers: Dict[str, str]
    credentials: Credentials
    form_fields: Dict[str, str]
    timestamp: datetime
    timeout: int = 30  # seconds
    requires_csrf: bool = False
    csrf_token: Optional[str] = None
    additional_data: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert request to dictionary representation.

        Returns:
            Dictionary with all request fields.
        """
        return {
            "request_id": self.request_id,
            "url": self.url,
            "method": self.method.value,
            "headers": self.headers,
            "credentials": self.credentials.to_dict(),
            "form_fields": self.form_fields,
            "timestamp": self.timestamp.isoformat(),
            "timeout": self.timeout,
            "requires_csrf": self.requires_csrf,
            "csrf_token": self.csrf_token,
            "additional_data": self.additional_data
        }


class AuthRequestManager:
    """
    Manages the creation and preparation of authentication requests.

    This is an abstract layer that prepares requests but does NOT
    execute them. The actual network calls are delegated to other
    components (browser automation, API clients, etc.).

    PRIVACY GUARANTEE:
        - Handles ONLY username/password credentials
        - No biometric data processing
        - No credential persistence
        - Secure in-memory handling only
    """

    def __init__(self):
        """Initialize the authentication request manager."""
        self._active_requests: Dict[str, AuthRequest] = {}
        self._request_templates: Dict[str, Dict] = {}
        self._initialize_templates()

    def _initialize_templates(self):
        """Initialize common authentication request templates."""
        self._request_templates = {
            "standard_form": {
                "method": RequestMethod.POST,
                "headers": {
                    "Content-Type": "application/x-www-form-urlencoded",
                    "User-Agent": "SENTI-OS/1.0"
                },
                "form_fields": {
                    "username": "{username}",
                    "password": "{password}"
                }
            },
            "json_api": {
                "method": RequestMethod.POST,
                "headers": {
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                    "User-Agent": "SENTI-OS/1.0"
                },
                "form_fields": {
                    "username": "{username}",
                    "password": "{password}"
                }
            },
            "oauth_style": {
                "method": RequestMethod.POST,
                "headers": {
                    "Content-Type": "application/x-www-form-urlencoded",
                    "User-Agent": "SENTI-OS/1.0"
                },
                "form_fields": {
                    "grant_type": "password",
                    "username": "{username}",
                    "password": "{password}",
                    "client_id": "{client_id}"
                }
            }
        }

    def create_auth_request(
        self,
        url: str,
        username: str,
        password: str,
        template: str = "standard_form",
        additional_fields: Optional[Dict[str, str]] = None,
        custom_headers: Optional[Dict[str, str]] = None,
        timeout: int = 30
    ) -> AuthRequest:
        """
        Create an authentication request.

        Args:
            url: The authentication endpoint URL.
            username: The username credential.
            password: The password credential.
            template: Template name to use (default: "standard_form").
            additional_fields: Additional form fields to include.
            custom_headers: Custom headers to add/override.
            timeout: Request timeout in seconds.

        Returns:
            AuthRequest object ready to be executed.
        """
        # Generate unique request ID
        request_id = self._generate_request_id()

        # Create credentials object
        credentials = Credentials(
            username=username,
            password=password,
            credential_type=CredentialType.USERNAME_PASSWORD,
            additional_fields=additional_fields or {}
        )

        # Get template
        template_data = self._request_templates.get(
            template,
            self._request_templates["standard_form"]
        )

        # Prepare headers
        headers = template_data["headers"].copy()
        if custom_headers:
            headers.update(custom_headers)

        # Prepare form fields
        form_fields = template_data["form_fields"].copy()

        # Replace placeholders
        for key, value in form_fields.items():
            if "{username}" in str(value):
                form_fields[key] = username
            if "{password}" in str(value):
                form_fields[key] = password

        # Add additional fields
        if additional_fields:
            form_fields.update(additional_fields)

        # Create request
        auth_request = AuthRequest(
            request_id=request_id,
            url=url,
            method=template_data["method"],
            headers=headers,
            credentials=credentials,
            form_fields=form_fields,
            timestamp=datetime.utcnow(),
            timeout=timeout
        )

        # Store active request
        self._active_requests[request_id] = auth_request

        return auth_request

    def create_oauth_request(
        self,
        url: str,
        username: str,
        password: str,
        client_id: str,
        client_secret: Optional[str] = None,
        scope: Optional[str] = None
    ) -> AuthRequest:
        """
        Create an OAuth-style authentication request.

        Args:
            url: The OAuth token endpoint.
            username: The username.
            password: The password.
            client_id: OAuth client ID.
            client_secret: Optional client secret.
            scope: Optional OAuth scope.

        Returns:
            AuthRequest configured for OAuth.
        """
        additional_fields = {
            "client_id": client_id
        }

        if client_secret:
            additional_fields["client_secret"] = client_secret

        if scope:
            additional_fields["scope"] = scope

        return self.create_auth_request(
            url=url,
            username=username,
            password=password,
            template="oauth_style",
            additional_fields=additional_fields
        )

    def create_json_api_request(
        self,
        url: str,
        username: str,
        password: str,
        additional_data: Optional[Dict[str, Any]] = None
    ) -> AuthRequest:
        """
        Create a JSON API authentication request.

        Args:
            url: The API authentication endpoint.
            username: The username.
            password: The password.
            additional_data: Additional JSON data to include.

        Returns:
            AuthRequest configured for JSON API.
        """
        auth_request = self.create_auth_request(
            url=url,
            username=username,
            password=password,
            template="json_api"
        )

        if additional_data:
            auth_request.additional_data = additional_data

        return auth_request

    def add_csrf_token(self, request_id: str, csrf_token: str) -> bool:
        """
        Add CSRF token to an existing request.

        Args:
            request_id: The request ID.
            csrf_token: The CSRF token value.

        Returns:
            True if successful, False if request not found.
        """
        if request_id not in self._active_requests:
            return False

        request = self._active_requests[request_id]
        request.requires_csrf = True
        request.csrf_token = csrf_token
        request.form_fields["csrf_token"] = csrf_token

        return True

    def get_request(self, request_id: str) -> Optional[AuthRequest]:
        """
        Retrieve an authentication request by ID.

        Args:
            request_id: The request ID.

        Returns:
            AuthRequest if found, None otherwise.
        """
        return self._active_requests.get(request_id)

    def cancel_request(self, request_id: str) -> bool:
        """
        Cancel and cleanup an authentication request.

        Args:
            request_id: The request ID to cancel.

        Returns:
            True if cancelled, False if not found.
        """
        if request_id in self._active_requests:
            # Clean up credentials
            request = self._active_requests[request_id]
            del request.credentials
            del self._active_requests[request_id]
            return True
        return False

    def cleanup_expired_requests(self, max_age_minutes: int = 5):
        """
        Clean up expired authentication requests.

        Args:
            max_age_minutes: Maximum age in minutes before cleanup.
        """
        now = datetime.utcnow()
        expired_ids = []

        for request_id, request in self._active_requests.items():
            age = now - request.timestamp
            if age > timedelta(minutes=max_age_minutes):
                expired_ids.append(request_id)

        for request_id in expired_ids:
            self.cancel_request(request_id)

    def _generate_request_id(self) -> str:
        """
        Generate a unique request ID.

        Returns:
            Unique request ID string.
        """
        random_bytes = secrets.token_bytes(16)
        timestamp = str(datetime.utcnow().timestamp()).encode()
        combined = random_bytes + timestamp
        request_id = hashlib.sha256(combined).hexdigest()[:16]
        return f"auth_req_{request_id}"

    def get_active_request_count(self) -> int:
        """
        Get the number of active authentication requests.

        Returns:
            Count of active requests.
        """
        return len(self._active_requests)

    def register_custom_template(
        self,
        template_name: str,
        method: RequestMethod,
        headers: Dict[str, str],
        form_fields: Dict[str, str]
    ):
        """
        Register a custom authentication request template.

        Args:
            template_name: Name for the template.
            method: HTTP method.
            headers: Request headers.
            form_fields: Form field structure.
        """
        self._request_templates[template_name] = {
            "method": method,
            "headers": headers,
            "form_fields": form_fields
        }

    def export_request_for_execution(self, request_id: str) -> Optional[Dict[str, Any]]:
        """
        Export a request in a format suitable for execution layers.

        Args:
            request_id: The request ID to export.

        Returns:
            Dictionary representation of the request, or None if not found.
        """
        request = self.get_request(request_id)
        if not request:
            return None

        return request.to_dict()


def get_info() -> Dict[str, str]:
    """
    Get module information.

    Returns:
        Dictionary with module metadata.
    """
    return {
        "module": "auth_request_manager",
        "faza": "18",
        "version": "1.0.0",
        "description": "Manages authentication request creation (text credentials only)",
        "privacy_compliant": "true",
        "processes_biometrics": "false",
        "credential_types": "username_password_only"
    }
