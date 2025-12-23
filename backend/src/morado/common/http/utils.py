"""Utility functions for HTTP client.

This module provides utility functions for:
- Variable resolution in templates
- URL building with path parameters
- Query parameter encoding
- Request body serialization
- Sensitive information masking
"""

import json
import re
from typing import Any
from urllib.parse import urlencode

from .exceptions import VariableResolutionError


def resolve_variables(template: str, context: dict[str, Any]) -> str:
    """Resolve variable placeholders in a template string.

    Variables are specified using ${variable_name} syntax. The function
    replaces all placeholders with their corresponding values from the context.

    Args:
        template: Template string containing ${variable} placeholders
        context: Dictionary mapping variable names to their values

    Returns:
        String with all variables resolved

    Raises:
        VariableResolutionError: If any variable is not found in context

    Examples:
        >>> resolve_variables("Hello ${name}!", {"name": "World"})
        'Hello World!'
        >>> resolve_variables("${protocol}://${host}:${port}",
        ...                   {"protocol": "https", "host": "api.example.com", "port": 443})
        'https://api.example.com:443'
    """
    if not template:
        return template

    pattern = r'\$\{([^}]+)\}'
    missing_vars = []

    def replace_var(match: re.Match) -> str:
        var_name = match.group(1).strip()
        if var_name not in context:
            missing_vars.append(var_name)
            return match.group(0)  # Keep original placeholder
        return str(context[var_name])

    result = re.sub(pattern, replace_var, template)

    if missing_vars:
        msg = f"Variables not found in context: {', '.join(missing_vars)}"
        raise VariableResolutionError(
            msg,
            missing_vars=missing_vars
        )

    return result


def build_url(
    base_url: str,
    path: str,
    path_params: dict[str, Any] | None = None
) -> str:
    """Build a complete URL with path parameter substitution.

    Path parameters can be specified in two ways:
    1. Using {param_name} syntax (standard)
    2. Using :param_name syntax (common in REST frameworks)

    Args:
        base_url: Base URL (e.g., "https://api.example.com")
        path: URL path with optional parameter placeholders (e.g., "/users/{id}")
        path_params: Dictionary of path parameter values

    Returns:
        Complete URL with path parameters substituted

    Examples:
        >>> build_url("https://api.example.com", "/users/{id}", {"id": 123})
        'https://api.example.com/users/123'
        >>> build_url("https://api.example.com", "/users/:id/posts/:post_id",
        ...           {"id": 123, "post_id": 456})
        'https://api.example.com/users/123/posts/456'
    """
    # Remove trailing slash from base_url
    base_url = base_url.rstrip('/')

    # Ensure path starts with /
    if not path.startswith('/'):
        path = '/' + path

    # Replace path parameters if provided
    if path_params:
        # Replace {param} style
        for key, value in path_params.items():
            path = path.replace(f'{{{key}}}', str(value))
            # Also replace :param style
            path = path.replace(f':{key}', str(value))

    return base_url + path


def encode_query_params(params: dict[str, Any]) -> str:
    """Encode query parameters for URL.

    Handles various data types and properly encodes special characters.
    None values are skipped. Lists are encoded as multiple parameters with the same key.

    Args:
        params: Dictionary of query parameters

    Returns:
        URL-encoded query string (without leading '?')

    Examples:
        >>> encode_query_params({"name": "John Doe", "age": 30})
        'name=John+Doe&age=30'
        >>> encode_query_params({"tags": ["python", "http"], "active": True})
        'tags=python&tags=http&active=True'
    """
    if not params:
        return ""

    # Filter out None values
    filtered_params = {k: v for k, v in params.items() if v is not None}

    # Handle lists - expand them into multiple parameters
    expanded_params = []
    for key, value in filtered_params.items():
        if isinstance(value, (list, tuple)):
            for item in value:
                expanded_params.append((key, str(item)))
        else:
            expanded_params.append((key, str(value)))

    return urlencode(expanded_params)


def serialize_body(
    data: Any,
    content_type: str | None = None
) -> tuple[Any, str]:
    """Serialize request body based on content type.

    Automatically determines serialization format based on content type.
    Supports JSON, form data, and raw data.

    Args:
        data: Data to serialize
        content_type: Content-Type header value (optional)

    Returns:
        Tuple of (serialized_data, content_type)

    Examples:
        >>> serialize_body({"name": "John"}, "application/json")
        ('{"name": "John"}', 'application/json')
        >>> serialize_body({"name": "John"}, "application/x-www-form-urlencoded")
        ('name=John', 'application/x-www-form-urlencoded')
    """
    if data is None:
        return None, content_type or "text/plain"

    # If data is already a string or bytes, return as-is
    if isinstance(data, (str, bytes)):
        return data, content_type or "text/plain"

    # Determine content type if not provided
    if content_type is None:
        # Default to JSON for dict/list
        if isinstance(data, (dict, list)):
            content_type = "application/json"
        else:
            content_type = "text/plain"

    # Serialize based on content type
    content_type_lower = content_type.lower()

    if "application/json" in content_type_lower:
        # Serialize as JSON
        serialized = json.dumps(data, ensure_ascii=False)
        return serialized, content_type

    elif "application/x-www-form-urlencoded" in content_type_lower:
        # Serialize as form data
        if isinstance(data, dict):
            serialized = urlencode(data)
            return serialized, content_type
        else:
            # If not a dict, convert to string
            return str(data), content_type

    elif "multipart/form-data" in content_type_lower:
        # For multipart, return data as-is (requests library handles it)
        return data, content_type

    # For other content types, convert to string
    elif isinstance(data, (dict, list)):
        # If it's structured data, serialize as JSON
        serialized = json.dumps(data, ensure_ascii=False)
        return serialized, content_type
    else:
        return str(data), content_type


def mask_sensitive_data(
    data: Any,
    sensitive_keys: list[str] | None = None,
    mask_value: str = "***"
) -> Any:
    """Mask sensitive information in data structures.

    Recursively traverses dictionaries and lists to mask sensitive values.
    Common sensitive keys are masked by default (password, token, secret, etc.).

    Args:
        data: Data structure to mask (dict, list, or primitive)
        sensitive_keys: List of keys to mask (case-insensitive)
        mask_value: Value to use for masking (default: "***")

    Returns:
        Copy of data with sensitive values masked

    Examples:
        >>> mask_sensitive_data({"username": "john", "password": "secret123"})
        {'username': 'john', 'password': '***'}
        >>> mask_sensitive_data({"api_key": "abc123", "data": "public"})
        {'api_key': '***', 'data': 'public'}
    """
    # Default sensitive keys (case-insensitive)
    default_sensitive_keys = {
        "password", "passwd", "pwd",
        "secret", "api_key", "apikey", "api-key",
        "token", "access_token", "refresh_token",
        "authorization", "auth",
        "cookie", "session",
        "private_key", "privatekey",
        "credit_card", "creditcard", "card_number",
        "ssn", "social_security"
    }

    # Combine with user-provided keys
    if sensitive_keys:
        all_sensitive_keys = default_sensitive_keys | {k.lower() for k in sensitive_keys}
    else:
        all_sensitive_keys = default_sensitive_keys

    def _mask_recursive(obj: Any) -> Any:
        """Recursively mask sensitive data."""
        if isinstance(obj, dict):
            masked = {}
            for key, value in obj.items():
                # Check if key is sensitive (case-insensitive)
                if key.lower() in all_sensitive_keys:
                    masked[key] = mask_value
                else:
                    masked[key] = _mask_recursive(value)
            return masked

        elif isinstance(obj, (list, tuple)):
            # Recursively mask list items
            masked_list = [_mask_recursive(item) for item in obj]
            return type(obj)(masked_list)  # Preserve list/tuple type

        else:
            # Return primitive values as-is
            return obj

    return _mask_recursive(data)


def mask_sensitive_headers(
    headers: dict[str, str],
    mask_value: str = "***"
) -> dict[str, str]:
    """Mask sensitive HTTP headers.

    Creates a copy of headers with sensitive values masked.
    Common sensitive headers are masked by default.

    Args:
        headers: Dictionary of HTTP headers
        mask_value: Value to use for masking (default: "***")

    Returns:
        Copy of headers with sensitive values masked

    Examples:
        >>> mask_sensitive_headers({"Content-Type": "application/json",
        ...                         "Authorization": "Bearer token123"})
        {'Content-Type': 'application/json', 'Authorization': '***'}
    """
    sensitive_header_names = {
        "authorization",
        "cookie",
        "set-cookie",
        "x-api-key",
        "api-key",
        "x-auth-token",
        "proxy-authorization"
    }

    masked = {}
    for key, value in headers.items():
        if key.lower() in sensitive_header_names:
            masked[key] = mask_value
        else:
            masked[key] = value

    return masked


def truncate_for_logging(
    data: Any,
    max_size: int = 1024
) -> str:
    """Truncate data for logging purposes.

    Converts data to string and truncates if it exceeds max_size.
    Adds a marker to indicate truncation.

    Args:
        data: Data to truncate
        max_size: Maximum size in characters

    Returns:
        Truncated string representation

    Examples:
        >>> truncate_for_logging("short text", max_size=100)
        'short text'
        >>> truncate_for_logging("x" * 2000, max_size=10)
        'xxxxxxxxxx... [truncated, total size: 2000]'
    """
    if data is None:
        return "None"

    # Convert to string
    if isinstance(data, bytes):
        try:
            data_str = data.decode('utf-8')
        except UnicodeDecodeError:
            data_str = f"<binary data, {len(data)} bytes>"
    elif isinstance(data, str):
        data_str = data
    else:
        try:
            data_str = json.dumps(data, ensure_ascii=False)
        except (TypeError, ValueError):
            data_str = str(data)

    # Truncate if necessary
    if len(data_str) > max_size:
        return f"{data_str[:max_size]}... [truncated, total size: {len(data_str)}]"

    return data_str
