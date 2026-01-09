"""
Validation utilities for Docker management tasks
"""
import re
from typing import Optional


def validate_stack_name(name: str) -> bool:
    """
    Validate stack name follows conventions: lowercase with underscores

    Args:
        name: Stack name to validate

    Returns:
        True if valid, False otherwise
    """
    pattern = r'^[a-z0-9_]+$'
    return bool(re.match(pattern, name))


def validate_container_name(name: str) -> bool:
    """
    Validate container name follows conventions: lowercase with hyphens

    Args:
        name: Container name to validate

    Returns:
        True if valid, False otherwise
    """
    pattern = r'^[a-z0-9-]+$'
    return bool(re.match(pattern, name))


def validate_port(port: int) -> bool:
    """
    Validate port number is in valid range

    Args:
        port: Port number to validate

    Returns:
        True if valid, False otherwise
    """
    return 1 <= port <= 65535


def validate_domain(domain: str) -> bool:
    """
    Validate domain name format

    Args:
        domain: Domain name to validate

    Returns:
        True if valid, False otherwise
    """
    pattern = r'^[a-z0-9]([a-z0-9-]{0,61}[a-z0-9])?(\.[a-z0-9]([a-z0-9-]{0,61}[a-z0-9])?)*$'
    return bool(re.match(pattern, domain.lower()))


def sanitize_name(name: str, separator: str = "-") -> str:
    """
    Sanitize a name to follow Docker naming conventions

    Args:
        name: Name to sanitize
        separator: Character to use as separator (default: "-")

    Returns:
        Sanitized name
    """
    # Convert to lowercase
    name = name.lower()

    # Replace spaces and invalid characters with separator
    name = re.sub(r'[^a-z0-9_-]+', separator, name)

    # Remove duplicate separators
    name = re.sub(f'{separator}+', separator, name)

    # Remove leading/trailing separators
    name = name.strip(separator)

    return name


def validate_job_id(job_id: str) -> bool:
    """
    Validate job ID format (UUID)

    Args:
        job_id: Job ID to validate

    Returns:
        True if valid UUID format, False otherwise
    """
    uuid_pattern = r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
    return bool(re.match(uuid_pattern, job_id.lower()))


def extract_service_name_from_domain(domain: str, suffix: str = ".bramleyvale.com") -> Optional[str]:
    """
    Extract service name from a domain

    Args:
        domain: Full domain name
        suffix: Domain suffix to remove

    Returns:
        Service name or None if invalid
    """
    if not domain.endswith(suffix):
        return None

    service_name = domain[:-len(suffix)]

    if validate_container_name(service_name):
        return service_name

    return None
