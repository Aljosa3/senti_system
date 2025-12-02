"""
FAZA 18 - Platform Detector Module

This module identifies external platforms (bank portals, eUprava, TRR portals, etc.)
and detects whether login steps require biometrics or other authentication methods.

CRITICAL PRIVACY RULE:
    This module NEVER processes biometric data.
    It only DETECTS that biometrics are required by the external platform.

Author: SENTI OS Core Team
License: Proprietary
GDPR/ZVOP/EU AI Act Compliant
"""

from typing import Dict, List, Optional, Set
from enum import Enum
from dataclasses import dataclass
import re
from urllib.parse import urlparse


class AuthMethod(Enum):
    """Enumeration of authentication methods that may be required."""
    PASSWORD = "password"
    OTP = "otp"  # One-Time Password
    BIOMETRIC = "biometric"  # External biometric (SENTI OS will NOT process)
    EMAIL_CODE = "email_code"
    SMS_CODE = "sms_code"
    OAUTH = "oauth"
    TWO_FACTOR = "two_factor"
    HARDWARE_TOKEN = "hardware_token"
    UNKNOWN = "unknown"


class PlatformType(Enum):
    """Types of external platforms."""
    BANK = "bank"
    GOVERNMENT = "government"  # eUprava, etc.
    PAYMENT = "payment"  # TRR portals, payment gateways
    HEALTHCARE = "healthcare"
    EDUCATION = "education"
    ENTERPRISE = "enterprise"
    GENERIC_WEB = "generic_web"
    UNKNOWN = "unknown"


@dataclass
class PlatformInfo:
    """Information about a detected platform."""
    platform_type: PlatformType
    platform_name: str
    url: str
    required_auth_methods: List[AuthMethod]
    requires_biometric: bool
    supports_password_only: bool
    estimated_wait_time: Optional[int] = None  # seconds
    notes: Optional[str] = None


class PlatformDetector:
    """
    Detects external platforms and their authentication requirements.

    This class analyzes URLs, page content, and metadata to identify
    what type of platform the user is interacting with and what
    authentication methods are required.

    PRIVACY GUARANTEE:
        This detector NEVER processes biometric data.
        It only identifies that biometrics are required externally.
    """

    def __init__(self):
        """Initialize the platform detector with known platform patterns."""
        self._platform_patterns = self._initialize_platform_patterns()
        self._auth_method_indicators = self._initialize_auth_indicators()

    def _initialize_platform_patterns(self) -> Dict[PlatformType, List[Dict]]:
        """
        Initialize patterns for known platforms.

        Returns:
            Dictionary mapping platform types to their detection patterns.
        """
        return {
            PlatformType.BANK: [
                {
                    "domains": ["nkbm.si", "nlb.si", "skb.si", "banka-intesa.si",
                                "addiko.si", "unicredit.si", "sberbank.si"],
                    "keywords": ["banka", "banking", "netbanking"],
                    "typical_auth": [AuthMethod.PASSWORD, AuthMethod.BIOMETRIC, AuthMethod.OTP]
                }
            ],
            PlatformType.GOVERNMENT: [
                {
                    "domains": ["euprava.si", "gov.si", "e-uprava.gov.si"],
                    "keywords": ["eUprava", "government", "vlada", "upravna"],
                    "typical_auth": [AuthMethod.PASSWORD, AuthMethod.BIOMETRIC, AuthMethod.TWO_FACTOR]
                }
            ],
            PlatformType.PAYMENT: [
                {
                    "domains": ["paypal.com", "stripe.com", "moneta.si"],
                    "keywords": ["payment", "transaction", "TRR", "plačilo"],
                    "typical_auth": [AuthMethod.PASSWORD, AuthMethod.OTP, AuthMethod.EMAIL_CODE]
                }
            ],
            PlatformType.HEALTHCARE: [
                {
                    "domains": ["zzzs.si", "nijz.si"],
                    "keywords": ["zdravstvo", "health", "medical"],
                    "typical_auth": [AuthMethod.PASSWORD, AuthMethod.BIOMETRIC]
                }
            ],
            PlatformType.EDUCATION: [
                {
                    "domains": ["edus.si", "arnes.si", "uni-lj.si"],
                    "keywords": ["education", "student", "šola", "univerza"],
                    "typical_auth": [AuthMethod.PASSWORD, AuthMethod.EMAIL_CODE]
                }
            ]
        }

    def _initialize_auth_indicators(self) -> Dict[AuthMethod, List[str]]:
        """
        Initialize indicators for detecting authentication methods.

        Returns:
            Dictionary mapping auth methods to detection keywords.
        """
        return {
            AuthMethod.BIOMETRIC: [
                "fingerprint", "face recognition", "facial recognition",
                "biometric", "touch id", "face id", "prstni odtis",
                "biometrija", "prepoznava obraza"
            ],
            AuthMethod.OTP: [
                "one-time password", "otp", "authenticator",
                "google authenticator", "token", "enkratno geslo"
            ],
            AuthMethod.EMAIL_CODE: [
                "email code", "verification code", "koda na email",
                "potrditvena koda"
            ],
            AuthMethod.SMS_CODE: [
                "sms code", "text message", "mobile code",
                "koda na telefon", "SMS koda"
            ],
            AuthMethod.TWO_FACTOR: [
                "two-factor", "2fa", "multi-factor", "mfa",
                "dvojna avtentikacija"
            ],
            AuthMethod.HARDWARE_TOKEN: [
                "hardware token", "security key", "yubikey",
                "fizični token", "varnostni ključ"
            ]
        }

    def detect_platform(self, url: str, page_content: Optional[str] = None,
                       page_metadata: Optional[Dict] = None) -> PlatformInfo:
        """
        Detect platform type and authentication requirements.

        Args:
            url: The URL of the platform.
            page_content: Optional page HTML/text content for analysis.
            page_metadata: Optional metadata (title, meta tags, etc.).

        Returns:
            PlatformInfo object with detected information.
        """
        parsed_url = urlparse(url)
        domain = parsed_url.netloc.lower()

        # Detect platform type
        platform_type = self._detect_platform_type(domain, page_content, page_metadata)
        platform_name = self._extract_platform_name(domain, page_metadata)

        # Detect required authentication methods
        required_auth_methods = self._detect_auth_methods(
            domain, page_content, page_metadata, platform_type
        )

        # Check if biometric is required
        requires_biometric = AuthMethod.BIOMETRIC in required_auth_methods

        # Check if password-only is supported
        supports_password_only = (
            AuthMethod.PASSWORD in required_auth_methods and
            len(required_auth_methods) == 1
        )

        # Estimate wait time for biometric authentication
        estimated_wait_time = self._estimate_wait_time(required_auth_methods)

        return PlatformInfo(
            platform_type=platform_type,
            platform_name=platform_name,
            url=url,
            required_auth_methods=required_auth_methods,
            requires_biometric=requires_biometric,
            supports_password_only=supports_password_only,
            estimated_wait_time=estimated_wait_time,
            notes=self._generate_notes(required_auth_methods)
        )

    def _detect_platform_type(self, domain: str, page_content: Optional[str],
                             page_metadata: Optional[Dict]) -> PlatformType:
        """
        Detect the type of platform based on domain and content.

        Args:
            domain: The domain name.
            page_content: Optional page content.
            page_metadata: Optional metadata.

        Returns:
            Detected PlatformType.
        """
        # Check against known patterns
        for platform_type, patterns in self._platform_patterns.items():
            for pattern in patterns:
                # Check domain match
                for known_domain in pattern["domains"]:
                    if known_domain in domain:
                        return platform_type

                # Check keyword match in content
                if page_content:
                    page_content_lower = page_content.lower()
                    for keyword in pattern["keywords"]:
                        if keyword.lower() in page_content_lower:
                            return platform_type

        return PlatformType.GENERIC_WEB

    def _extract_platform_name(self, domain: str,
                               page_metadata: Optional[Dict]) -> str:
        """
        Extract a human-readable platform name.

        Args:
            domain: The domain name.
            page_metadata: Optional metadata with title, etc.

        Returns:
            Platform name string.
        """
        if page_metadata and "title" in page_metadata:
            return page_metadata["title"]

        # Extract from domain
        parts = domain.split(".")
        if len(parts) >= 2:
            return parts[-2].upper()

        return domain

    def _detect_auth_methods(self, domain: str, page_content: Optional[str],
                            page_metadata: Optional[Dict],
                            platform_type: PlatformType) -> List[AuthMethod]:
        """
        Detect which authentication methods are required.

        Args:
            domain: The domain name.
            page_content: Optional page content.
            page_metadata: Optional metadata.
            platform_type: The detected platform type.

        Returns:
            List of required AuthMethod enums.
        """
        detected_methods: Set[AuthMethod] = set()

        # Start with typical methods for platform type
        for patterns in self._platform_patterns.get(platform_type, []):
            detected_methods.update(patterns.get("typical_auth", []))

        # Analyze page content for specific indicators
        if page_content:
            page_content_lower = page_content.lower()
            for auth_method, indicators in self._auth_method_indicators.items():
                for indicator in indicators:
                    if indicator.lower() in page_content_lower:
                        detected_methods.add(auth_method)

        # Always assume password is an option if nothing detected
        if not detected_methods:
            detected_methods.add(AuthMethod.PASSWORD)

        return sorted(list(detected_methods), key=lambda x: x.value)

    def _estimate_wait_time(self, auth_methods: List[AuthMethod]) -> Optional[int]:
        """
        Estimate wait time in seconds for authentication.

        Args:
            auth_methods: List of required authentication methods.

        Returns:
            Estimated wait time in seconds, or None if unknown.
        """
        if AuthMethod.BIOMETRIC in auth_methods:
            return 30  # 30 seconds for biometric + fallback
        elif AuthMethod.OTP in auth_methods:
            return 60  # 60 seconds for OTP entry
        elif AuthMethod.EMAIL_CODE in auth_methods:
            return 120  # 2 minutes for email code
        elif AuthMethod.SMS_CODE in auth_methods:
            return 90  # 90 seconds for SMS code
        else:
            return 15  # 15 seconds for basic password

    def _generate_notes(self, auth_methods: List[AuthMethod]) -> str:
        """
        Generate helpful notes about authentication flow.

        Args:
            auth_methods: List of required authentication methods.

        Returns:
            Notes string.
        """
        notes = []

        if AuthMethod.BIOMETRIC in auth_methods:
            notes.append(
                "BIOMETRIC DETECTED: SENTI OS will pause and hand control to "
                "the external platform for biometric verification."
            )

        if AuthMethod.OTP in auth_methods:
            notes.append(
                "OTP REQUIRED: User will need their authenticator app."
            )

        if len(auth_methods) > 2:
            notes.append(
                "MULTI-STEP AUTH: This platform requires multiple authentication steps."
            )

        return " ".join(notes) if notes else "Standard authentication flow."

    def is_biometric_required(self, url: str, page_content: Optional[str] = None) -> bool:
        """
        Quick check: does this platform require biometrics?

        Args:
            url: The URL to check.
            page_content: Optional page content.

        Returns:
            True if biometrics are required.
        """
        platform_info = self.detect_platform(url, page_content)
        return platform_info.requires_biometric

    def get_supported_auth_methods(self, url: str) -> List[AuthMethod]:
        """
        Get list of supported authentication methods for a platform.

        Args:
            url: The URL of the platform.

        Returns:
            List of supported AuthMethod enums.
        """
        platform_info = self.detect_platform(url)
        return platform_info.required_auth_methods

    def can_use_password_only(self, url: str) -> bool:
        """
        Check if platform supports password-only authentication.

        Args:
            url: The URL to check.

        Returns:
            True if password-only is supported.
        """
        platform_info = self.detect_platform(url)
        return platform_info.supports_password_only


def get_info() -> Dict[str, str]:
    """
    Get module information.

    Returns:
        Dictionary with module metadata.
    """
    return {
        "module": "platform_detector",
        "faza": "18",
        "version": "1.0.0",
        "description": "Detects external platforms and authentication requirements",
        "privacy_compliant": "true",
        "processes_biometrics": "false"
    }
