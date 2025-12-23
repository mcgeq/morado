# HTTP Client File Operations Implementation

## Overview

This document describes the file operations support implemented for the HTTP client wrapper, fulfilling Requirements 9.1-9.5.

## Implementation Summary

### 1. File Upload Methods (HttpClient)

#### `upload_file()` - Single File Upload (Requirement 9.1)
```python
def upload_file(
    self,
    url: str,
    file_path: str,
    file_field_name: str = "file",
    additional_fields: Optional[dict[str, Any]] = None,
    **kwargs: Any,
) -> HttpResponse
```

**Features:**
- Uploads a single file using multipart/form-data
- Automatically opens and reads the file
- Supports custom field names
- Can include additional form fields
- Raises FileNotFoundError if file doesn't exist

**Example:**
```python
client = HttpClient()
response = client.upload_file(
    "https://api.example.com/upload",
    "/path/to/document.pdf",
    file_field_name="document",
    additional_fields={"description": "My document"}
)
```

#### `upload_files()` - Multiple File Upload (Requirement 9.2)
```python
def upload_files(
    self,
    url: str,
    files: dict[str, str],
    additional_fields: Optional[dict[str, Any]] = None,
    **kwargs: Any,
) -> HttpResponse
```

**Features:**
- Uploads multiple files in a single request
- Uses multipart/form-data format
- Automatically manages file handles
- Ensures proper cleanup even on errors
- Can include additional form fields

**Example:**
```python
client = HttpClient()
response = client.upload_files(
    "https://api.example.com/upload",
    files={
        "document": "/path/to/document.pdf",
        "image": "/path/to/image.png"
    },
    additional_fields={"description": "Multiple files"}
)
```

#### `upload_multipart()` - Advanced Multipart Upload (Requirement 9.3)
```python
def upload_multipart(
    self,
    url: str,
    files: Optional[dict[str, tuple[str, Any, Optional[str]]]] = None,
    data: Optional[dict[str, Any]] = None,
    **kwargs: Any,
) -> HttpResponse
```

**Features:**
- Full control over multipart uploads
- Specify custom filenames and content types
- Mix files with form fields
- Supports file handles, bytes, or strings
- Most flexible upload method

**Example:**
```python
client = HttpClient()
with open("/path/to/file.pdf", "rb") as f:
    response = client.upload_multipart(
        "https://api.example.com/upload",
        files={
            "document": ("report.pdf", f, "application/pdf"),
            "thumbnail": ("thumb.png", image_bytes, "image/png")
        },
        data={"title": "My Report", "category": "finance"}
    )
```

### 2. Streaming Download Methods (HttpResponse)

#### `iter_content()` - Stream Response Content (Requirement 9.4)
```python
def iter_content(self, chunk_size: int = 8192) -> Any
```

**Features:**
- Iterates over response content in chunks
- Avoids loading entire content into memory
- Ideal for large file downloads
- Configurable chunk size

**Example:**
```python
response = client.get("https://example.com/large-file.zip")
with open("large-file.zip", "wb") as f:
    for chunk in response.iter_content(chunk_size=8192):
        if chunk:
            f.write(chunk)
```

#### `save_to_file()` - Save Response to File (Requirement 9.5)
```python
def save_to_file(self, filepath: str, chunk_size: int = 8192) -> None
```

**Features:**
- Saves response content to a file
- Uses streaming for large files
- Creates parent directories automatically
- Configurable chunk size for memory efficiency

**Example:**
```python
response = client.get("https://example.com/file.pdf")
response.save_to_file("/path/to/save/file.pdf")
```

#### `stream_to_file()` - Stream with Byte Count
```python
def stream_to_file(self, filepath: str, chunk_size: int = 8192) -> int
```

**Features:**
- Similar to save_to_file but returns byte count
- Useful for progress tracking
- Uses streaming for efficiency

**Example:**
```python
response = client.get("https://example.com/large-file.zip")
bytes_written = response.stream_to_file("large-file.zip")
print(f"Downloaded {bytes_written} bytes")
```

## Requirements Validation

All requirements have been implemented and tested:

### ✓ Requirement 9.1: Single File Upload
- Implemented `upload_file()` method
- Uses multipart/form-data format
- Tested with httpbin.org

### ✓ Requirement 9.2: Multiple File Upload
- Implemented `upload_files()` method
- Handles multiple files in single request
- Proper file handle management

### ✓ Requirement 9.3: Mixed Upload
- Both `upload_file()` and `upload_files()` support additional form fields
- `upload_multipart()` provides full control
- Tested with files and form data together

### ✓ Requirement 9.4: Streaming Download
- Implemented `iter_content()` method
- Supports chunked reading
- Memory efficient for large files

### ✓ Requirement 9.5: File Save
- Enhanced `save_to_file()` with streaming
- Added `stream_to_file()` with byte count
- Creates directories automatically

## Testing

### Verification Scripts

1. **verify_file_operations.py** - Basic functionality tests
   - Method existence checks
   - Basic upload/download tests
   - Error handling verification

2. **test_file_operations_comprehensive.py** - Full requirement validation
   - Single file upload (9.1)
   - Multiple file upload (9.2)
   - Mixed upload (9.3)
   - Streaming download (9.4)
   - File save (9.5)
   - Advanced multipart upload

### Test Results

All tests passed successfully:
```
✓ 9.1 - Single file upload
✓ 9.2 - Multiple file upload
✓ 9.3 - Mixed file and form field upload
✓ 9.4 - Streaming download
✓ 9.5 - File save functionality
```

## Design Decisions

### 1. Automatic File Handle Management
- `upload_file()` and `upload_files()` automatically open and close files
- Ensures proper cleanup even on errors
- Simplifies API for common use cases

### 2. Three-Tier Upload API
- **Simple**: `upload_file()` for single files
- **Batch**: `upload_files()` for multiple files
- **Advanced**: `upload_multipart()` for full control

### 3. Streaming by Default
- `save_to_file()` uses streaming to handle large files
- Configurable chunk size (default: 8192 bytes)
- Memory efficient

### 4. Error Handling
- FileNotFoundError for missing files
- IOError for file write failures
- Proper cleanup in finally blocks

## Integration with Existing Code

The file operations integrate seamlessly with existing HTTP client features:

1. **Session Management**: File uploads use the same session and connection pool
2. **Retry Logic**: File operations respect retry configuration
3. **Interceptors**: Request/response interceptors work with file uploads
4. **Logging**: File operations are logged like other requests
5. **Tracing**: Request IDs are propagated in file upload requests

## Performance Considerations

1. **Memory Efficiency**: Streaming prevents loading large files into memory
2. **Connection Reuse**: Uses existing session connection pool
3. **Chunk Size**: Configurable for optimal performance (default: 8KB)
4. **File Handle Cleanup**: Automatic cleanup prevents resource leaks

## Security Considerations

1. **Path Validation**: File paths are validated before use
2. **Directory Creation**: Parent directories created safely
3. **Error Messages**: Don't expose sensitive file system information
4. **Content Type**: Can be explicitly specified to prevent MIME sniffing

## Future Enhancements

Potential improvements for future versions:

1. **Progress Callbacks**: Add progress tracking for large uploads/downloads
2. **Resumable Uploads**: Support for resuming interrupted uploads
3. **Compression**: Automatic compression for large files
4. **Async Support**: Async versions of file operations
5. **Multipart Streaming**: Stream large files during upload

## Examples

### Complete Upload Example
```python
from morado.common.http.client import HttpClient

# Create client
client = HttpClient(base_url="https://api.example.com")

# Upload single file with metadata
response = client.upload_file(
    "/documents/upload",
    "/path/to/report.pdf",
    file_field_name="document",
    additional_fields={
        "title": "Q4 Report",
        "category": "financial",
        "confidential": "true"
    }
)

print(f"Upload status: {response.status_code}")
print(f"Document ID: {response.json()['id']}")
```

### Complete Download Example
```python
from morado.common.http.client import HttpClient

# Create client
client = HttpClient()

# Download large file with streaming
response = client.get("https://example.com/large-dataset.zip")

# Save with progress tracking
bytes_written = response.stream_to_file("dataset.zip")
print(f"Downloaded {bytes_written / 1024 / 1024:.2f} MB")
```

### Batch Upload Example
```python
from morado.common.http.client import HttpClient

# Create client
client = HttpClient()

# Upload multiple files
response = client.upload_files(
    "https://api.example.com/batch-upload",
    files={
        "invoice": "/path/to/invoice.pdf",
        "receipt": "/path/to/receipt.jpg",
        "contract": "/path/to/contract.pdf"
    },
    additional_fields={
        "transaction_id": "TXN-12345",
        "customer_id": "CUST-67890"
    }
)

print(f"Batch upload complete: {response.status_code}")
```

## Conclusion

The file operations implementation provides a complete, robust, and user-friendly API for file uploads and downloads. All requirements (9.1-9.5) have been successfully implemented and tested. The implementation follows best practices for resource management, error handling, and integration with the existing HTTP client infrastructure.
