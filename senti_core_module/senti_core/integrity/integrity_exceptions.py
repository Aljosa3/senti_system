"""
FAZA 45 — Minimal Integrity Exceptions
"""


class IntegrityViolation(Exception):
    pass


class MissingIntegrityData(Exception):
    pass


class IntegrityStoreCorrupted(Exception):
    pass
