"""HTTP Client Usage Examples

This file contains practical examples of using the Morado HTTP Client Wrapper.
"""

from morado.common.http import (
    create_default_client,
    create_http_client,
    HttpClientConfig,
    load_config_from_dict,
)
from morado.common.http.interceptor import RequestInterceptor, ResponseInterceptor
from morado.common.http.response import HttpResponse
from typing import Any


# =============================================================================
# Basic Usage Examples
# =============================================================================

def example_basic_get():
    """Simple GET request."""
    client = create_default_client()
    
    try:
        response = client.get("https://jsonplaceholder.typicode.com/users")
        
        if response.is_success():
            users = response.json()
            print(f"Found {len(users)} users")
            for user in users[:3]:
                print(f"  - {user['name']} ({user['email']})")
        else:
            print(f"Request failed: {response.status_code}")
    finally:
        client.close()


def example_basic_post():
    """Simple POST request with JSON body."""
    client = create_default_client()
    
    try:
        new_user = {
            "name": "John Doe",
            "email": "john@example.com",
            "username": "johndoe"
        }
        
        response = client.post(
            "https://jsonplaceholder.typicode.com/users",
            json=new_user
        )
        
        if response.is_success():
            created_user = response.json()
            print(f"Created user with ID: {created_user['id']}")
        else:
            print(f"Failed to create user: {response.status_code}")
    finally:
        client.close()


def example_with_context_manager():
    """Using context manager for automatic cleanup."""
    with create_default_client() as client:
        response = client.get("https://jsonplaceholder.typicode.com/posts")
        posts = response.json()
        print(f"Found {len(posts)} posts")


# =============================================================================
# Configuration Examples
# =============================================================================

def example_custom_configuration():
    """Create client with custom configuration."""
    config = HttpClientConfig(
        base_url="https://jsonplaceholder.typicode.com",
        connect_timeout=15,
        read_timeout=60,
        max_retries=5,
        retry_strategy="exponential",
        enable_logging=True,
        enable_tracing=True
    )
    
    client = create_http_client(config)
    
    try:
        # Use relative URLs with base_url
        response = client.get("/users")
        print(f"Status: {response.status_code}")
    finally:
        client.close()


def example_configuration_from_dict():
    """Load configuration from dictionary."""
    config_dict = {
        "base_url": "https://jsonplaceholder.typicode.com",
        "connect_timeout": 10,
        "read_timeout": 30,
        "max_retries": 3,
        "retry_strategy": "exponential"
    }
    
    config = load_config_from_dict(config_dict)
    client = create_http_client(config)
    
    try:
        response = client.get("/posts")
        print(f"Found {len(response.json())} posts")
    finally:
        client.close()


# =============================================================================
# Request Examples
# =============================================================================

def example_query_parameters():
    """Send request with query parameters."""
    with create_default_client() as client:
        response = client.get(
            "https://jsonplaceholder.typicode.com/posts",
            params={
                "userId": 1,
                "_limit": 5
            }
        )
        
        posts = response.json()
        print(f"Found {len(posts)} posts for user 1")


def example_custom_headers():
    """Send request with custom headers."""
    with create_default_client() as client:
        response = client.get(
            "https://jsonplaceholder.typicode.com/posts",
            headers={
                "Accept": "application/json",
                "User-Agent": "MyApp/1.0"
            }
        )
        
        print(f"Status: {response.status_code}")


def example_form_data():
    """Send form data."""
    with create_default_client() as client:
        response = client.post(
            "https://httpbin.org/post",
            data={
                "username": "john",
                "password": "secret"
            }
        )
        
        result = response.json()
        print(f"Form data sent: {result['form']}")


def example_timeout_override():
    """Override timeout for specific request."""
    with create_default_client() as client:
        # Use longer timeout for slow endpoint
        response = client.get(
            "https://httpbin.org/delay/5",
            timeout=(10, 30)  # (connect_timeout, read_timeout)
        )
        
        print(f"Request completed in {response.request_time:.2f}s")


# =============================================================================
# Response Handling Examples
# =============================================================================

def example_response_properties():
    """Access response properties."""
    with create_default_client() as client:
        response = client.get("https://jsonplaceholder.typicode.com/users/1")
        
        # Status code
        print(f"Status: {response.status_code}")
        
        # Headers
        print(f"Content-Type: {response.get_header('Content-Type')}")
        
        # Body
        print(f"Text: {response.text[:100]}...")
        
        # JSON
        user = response.json()
        print(f"User: {user['name']}")
        
        # Request time
        print(f"Duration: {response.request_time:.2f}s")


def example_jsonpath_extraction():
    """Extract data using JSONPath."""
    with create_default_client() as client:
        response = client.get("https://jsonplaceholder.typicode.com/users")
        
        # Extract all names
        names = response.jsonpath("$[*].name")
        print(f"User names: {names}")
        
        # Extract first user's email
        first_email = response.jsonpath("$[0].email")
        print(f"First user email: {first_email}")


def example_error_handling():
    """Handle errors gracefully."""
    from morado.common.http import (
        HttpTimeoutError,
        HttpConnectionError,
        HttpRequestError
    )
    
    with create_default_client() as client:
        try:
            response = client.get("https://jsonplaceholder.typicode.com/users")
            response.raise_for_status()
            users = response.json()
            print(f"Success: {len(users)} users")
            
        except HttpTimeoutError as e:
            print(f"Request timed out: {e}")
        except HttpConnectionError as e:
            print(f"Connection failed: {e}")
        except HttpRequestError as e:
            print(f"Request failed: {e}")
        except Exception as e:
            print(f"Unexpected error: {e}")


# =============================================================================
# File Operations Examples
# =============================================================================

def example_file_upload():
    """Upload a single file."""
    with create_default_client() as client:
        # Create a test file
        test_file = "/tmp/test.txt"
        with open(test_file, "w") as f:
            f.write("Test content")
        
        # Upload file
        response = client.upload_file(
            "https://httpbin.org/post",
            test_file,
            file_field_name="file",
            additional_fields={
                "description": "Test file upload"
            }
        )
        
        result = response.json()
        print(f"File uploaded: {result['files']}")


def example_multiple_file_upload():
    """Upload multiple files."""
    with create_default_client() as client:
        # Create test files
        file1 = "/tmp/file1.txt"
        file2 = "/tmp/file2.txt"
        
        with open(file1, "w") as f:
            f.write("File 1 content")
        with open(file2, "w") as f:
            f.write("File 2 content")
        
        # Upload multiple files
        response = client.upload_files(
            "https://httpbin.org/post",
            files={
                "file1": file1,
                "file2": file2
            },
            additional_fields={
                "description": "Multiple files"
            }
        )
        
        result = response.json()
        print(f"Files uploaded: {result['files']}")


def example_file_download():
    """Download and save file."""
    with create_default_client() as client:
        response = client.get("https://httpbin.org/image/png")
        
        # Save to file
        output_path = "/tmp/downloaded_image.png"
        response.save_to_file(output_path)
        print(f"File saved to: {output_path}")


# =============================================================================
# Interceptor Examples
# =============================================================================

class AuthenticationInterceptor(RequestInterceptor):
    """Add authentication to all requests."""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
    
    def before_request(
        self,
        method: str,
        url: str,
        headers: dict[str, str],
        **kwargs: Any,
    ) -> tuple[str, str, dict[str, str], dict[str, Any]]:
        """Add API key header."""
        headers["X-API-Key"] = self.api_key
        return method, url, headers, kwargs


class LoggingResponseInterceptor(ResponseInterceptor):
    """Log response details."""
    
    def after_response(self, response: HttpResponse) -> HttpResponse:
        """Log response status."""
        print(f"Response: {response.status_code} in {response.request_time:.2f}s")
        return response


def example_custom_interceptors():
    """Use custom interceptors."""
    client = create_default_client()
    
    # Add authentication interceptor
    client.interceptor_manager.add_request_interceptor(
        AuthenticationInterceptor(api_key="my-secret-key")
    )
    
    # Add logging interceptor
    client.interceptor_manager.add_response_interceptor(
        LoggingResponseInterceptor()
    )
    
    try:
        # All requests will have API key and be logged
        response = client.get("https://httpbin.org/get")
        print(f"Status: {response.status_code}")
    finally:
        client.close()


# =============================================================================
# Advanced Examples
# =============================================================================

def example_api_client_class():
    """Create a reusable API client class."""
    
    class UserAPIClient:
        """Client for User API."""
        
        def __init__(self, base_url: str, api_key: str):
            self.client = create_default_client(base_url=base_url)
            self.api_key = api_key
        
        def _get_headers(self) -> dict[str, str]:
            """Get common headers."""
            return {
                "Authorization": f"Bearer {self.api_key}",
                "Accept": "application/json"
            }
        
        def get_user(self, user_id: int) -> dict:
            """Get user by ID."""
            response = self.client.get(
                f"/users/{user_id}",
                headers=self._get_headers()
            )
            response.raise_for_status()
            return response.json()
        
        def create_user(self, name: str, email: str) -> dict:
            """Create a new user."""
            response = self.client.post(
                "/users",
                json={"name": name, "email": email},
                headers=self._get_headers()
            )
            response.raise_for_status()
            return response.json()
        
        def list_users(self, page: int = 1, limit: int = 10) -> list[dict]:
            """List users with pagination."""
            response = self.client.get(
                "/users",
                params={"page": page, "limit": limit},
                headers=self._get_headers()
            )
            response.raise_for_status()
            return response.json()
        
        def close(self):
            """Close the client."""
            self.client.close()
    
    # Usage
    api = UserAPIClient(
        base_url="https://jsonplaceholder.typicode.com",
        api_key="my-api-key"
    )
    
    try:
        user = api.get_user(1)
        print(f"User: {user['name']}")
        
        users = api.list_users(page=1, limit=5)
        print(f"Found {len(users)} users")
    finally:
        api.close()


def example_pagination():
    """Fetch all pages of results."""
    
    def fetch_all_posts(client) -> list[dict]:
        """Fetch all posts with pagination."""
        all_posts = []
        page = 1
        limit = 10
        
        while True:
            response = client.get(
                "https://jsonplaceholder.typicode.com/posts",
                params={"_page": page, "_limit": limit}
            )
            
            posts = response.json()
            if not posts:
                break
            
            all_posts.extend(posts)
            page += 1
            
            # Safety limit
            if page > 100:
                break
        
        return all_posts
    
    with create_default_client() as client:
        posts = fetch_all_posts(client)
        print(f"Fetched {len(posts)} total posts")


def example_batch_requests():
    """Make multiple requests efficiently."""
    
    def batch_get_users(client, user_ids: list[int]) -> list[dict]:
        """Get multiple users by ID."""
        users = []
        
        for user_id in user_ids:
            try:
                response = client.get(
                    f"https://jsonplaceholder.typicode.com/users/{user_id}"
                )
                if response.is_success():
                    users.append(response.json())
            except Exception as e:
                print(f"Failed to get user {user_id}: {e}")
        
        return users
    
    with create_default_client() as client:
        user_ids = [1, 2, 3, 4, 5]
        users = batch_get_users(client, user_ids)
        print(f"Fetched {len(users)} users")


def example_retry_with_custom_logic():
    """Handle retries with custom logic."""
    from morado.common.http import RetryExhaustedError
    
    config = HttpClientConfig(
        enable_retry=True,
        max_retries=3,
        retry_strategy="exponential"
    )
    
    with create_http_client(config) as client:
        try:
            response = client.get("https://httpbin.org/status/500")
            print(f"Status: {response.status_code}")
        except RetryExhaustedError as e:
            print(f"All retries failed: {e}")
            print("Retry history:")
            for attempt in e.retry_history:
                print(f"  Attempt {attempt['attempt']}: {attempt['error']}")


# =============================================================================
# Main - Run Examples
# =============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("HTTP Client Examples")
    print("=" * 70)
    
    examples = [
        ("Basic GET", example_basic_get),
        ("Basic POST", example_basic_post),
        ("Context Manager", example_with_context_manager),
        ("Custom Configuration", example_custom_configuration),
        ("Query Parameters", example_query_parameters),
        ("Custom Headers", example_custom_headers),
        ("Response Properties", example_response_properties),
        ("Error Handling", example_error_handling),
        ("Custom Interceptors", example_custom_interceptors),
        ("API Client Class", example_api_client_class),
        ("Pagination", example_pagination),
    ]
    
    for name, example_func in examples:
        print(f"\n{name}")
        print("-" * 70)
        try:
            example_func()
        except Exception as e:
            print(f"Error: {e}")
        print()
