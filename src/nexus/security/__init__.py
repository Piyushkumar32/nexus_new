"""Security intelligence and defensive auditing."""

from nexus.security.auditor import (
    audit_listening_ports,
    audit_suspicious_processes,
    calculate_file_hash,
)

__all__ = ["audit_listening_ports", "audit_suspicious_processes", "calculate_file_hash"]