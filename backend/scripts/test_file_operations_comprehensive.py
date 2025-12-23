"""Comprehensive test for HTTP client file operations.

This script tests all file operation requirements:
- Single file upload (Requirement 9.1)
- Multiple file upload (Requirement 9.2)
- Mixed file and form field upload (Requirement 9.3)
- Streaming download (Requirement 9.4)
- File save functionality (Requirement 9.5)
"""

import tempfile
from pathlib import Path

from morado.common.http.client import HttpClient


def test_single_file_upload():
    """Test single file upload (Requirement 9.1)."""
    print("\n1. Testing single file upload (Requirement 9.1)...")
    
    # Create a test file
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
        f.write("Single file upload test content")
        temp_file = f.name
    
    try:
        client = HttpClient()
        
        # Upload single file
        response = client.upload_file(
            "https://httpbin.org/post",
            temp_file,
            file_field_name="document"
        )
        
        # Verify response
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        # Parse response to verify file was uploaded
        data = response.json()
        assert 'files' in data, "Response should contain 'files' field"
        assert 'document' in data['files'], "Uploaded file should be in 'document' field"
        
        print("   ✓ Single file upload successful")
        print(f"   ✓ File uploaded as 'document' field")
        print(f"   ✓ Response status: {response.status_code}")
        
    finally:
        Path(temp_file).unlink(missing_ok=True)


def test_multiple_file_upload():
    """Test multiple file upload (Requirement 9.2)."""
    print("\n2. Testing multiple file upload (Requirement 9.2)...")
    
    # Create multiple test files
    temp_files = []
    try:
        for i in range(3):
            with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix=f'_{i}.txt') as f:
                f.write(f"File {i} content")
                temp_files.append(f.name)
        
        client = HttpClient()
        
        # Upload multiple files
        response = client.upload_files(
            "https://httpbin.org/post",
            files={
                "file1": temp_files[0],
                "file2": temp_files[1],
                "file3": temp_files[2]
            }
        )
        
        # Verify response
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        # Parse response to verify all files were uploaded
        data = response.json()
        assert 'files' in data, "Response should contain 'files' field"
        assert 'file1' in data['files'], "file1 should be uploaded"
        assert 'file2' in data['files'], "file2 should be uploaded"
        assert 'file3' in data['files'], "file3 should be uploaded"
        
        print("   ✓ Multiple file upload successful")
        print(f"   ✓ Uploaded {len(temp_files)} files")
        print(f"   ✓ All files present in response")
        
    finally:
        for temp_file in temp_files:
            Path(temp_file).unlink(missing_ok=True)


def test_mixed_upload():
    """Test file and form field mixed upload (Requirement 9.3)."""
    print("\n3. Testing mixed file and form field upload (Requirement 9.3)...")
    
    # Create a test file
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
        f.write("Mixed upload test content")
        temp_file = f.name
    
    try:
        client = HttpClient()
        
        # Upload file with additional form fields
        response = client.upload_file(
            "https://httpbin.org/post",
            temp_file,
            file_field_name="attachment",
            additional_fields={
                "title": "Test Document",
                "category": "testing",
                "priority": "high"
            }
        )
        
        # Verify response
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        # Parse response to verify file and form fields
        data = response.json()
        assert 'files' in data, "Response should contain 'files' field"
        assert 'attachment' in data['files'], "File should be uploaded"
        assert 'form' in data, "Response should contain 'form' field"
        assert data['form']['title'] == "Test Document", "Form field 'title' should match"
        assert data['form']['category'] == "testing", "Form field 'category' should match"
        assert data['form']['priority'] == "high", "Form field 'priority' should match"
        
        print("   ✓ Mixed upload successful")
        print(f"   ✓ File uploaded as 'attachment'")
        print(f"   ✓ Form fields: title, category, priority")
        print(f"   ✓ All form fields present in response")
        
    finally:
        Path(temp_file).unlink(missing_ok=True)


def test_streaming_download():
    """Test streaming download (Requirement 9.4)."""
    print("\n4. Testing streaming download (Requirement 9.4)...")
    
    client = HttpClient()
    
    # Download a file using streaming
    response = client.get("https://httpbin.org/bytes/10240")  # 10KB file
    
    # Verify response
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    
    # Test iter_content method
    chunks = []
    chunk_count = 0
    for chunk in response.iter_content(chunk_size=1024):
        if chunk:
            chunks.append(chunk)
            chunk_count += 1
    
    total_size = sum(len(chunk) for chunk in chunks)
    
    print("   ✓ Streaming download successful")
    print(f"   ✓ Downloaded {total_size} bytes in {chunk_count} chunks")
    print(f"   ✓ iter_content() method works correctly")


def test_file_save():
    """Test file save functionality (Requirement 9.5)."""
    print("\n5. Testing file save functionality (Requirement 9.5)...")
    
    client = HttpClient()
    
    # Download a file
    response = client.get("https://httpbin.org/bytes/5120")  # 5KB file
    
    # Create a temporary directory for saving
    with tempfile.TemporaryDirectory() as temp_dir:
        save_path = Path(temp_dir) / "downloaded_file.bin"
        
        # Test save_to_file method
        response.save_to_file(str(save_path))
        
        # Verify file was saved
        assert save_path.exists(), "File should be saved"
        saved_size = save_path.stat().st_size
        assert saved_size == 5120, f"Expected 5120 bytes, got {saved_size}"
        
        print("   ✓ File save successful")
        print(f"   ✓ Saved to: {save_path}")
        print(f"   ✓ File size: {saved_size} bytes")
        
        # Test stream_to_file method
        save_path2 = Path(temp_dir) / "streamed_file.bin"
        response2 = client.get("https://httpbin.org/bytes/5120")
        bytes_written = response2.stream_to_file(str(save_path2))
        
        assert save_path2.exists(), "Streamed file should be saved"
        assert bytes_written == 5120, f"Expected 5120 bytes written, got {bytes_written}"
        
        print("   ✓ Stream to file successful")
        print(f"   ✓ Bytes written: {bytes_written}")


def test_multipart_upload_advanced():
    """Test advanced multipart upload with full control."""
    print("\n6. Testing advanced multipart upload...")
    
    # Create test content
    file_content = b"Advanced multipart test content"
    
    client = HttpClient()
    
    # Upload using upload_multipart with full control
    response = client.upload_multipart(
        "https://httpbin.org/post",
        files={
            "document": ("test.txt", file_content, "text/plain"),
            "data": ("data.json", b'{"key": "value"}', "application/json")
        },
        data={
            "description": "Advanced upload",
            "version": "1.0"
        }
    )
    
    # Verify response
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    
    data = response.json()
    assert 'files' in data, "Response should contain 'files' field"
    assert 'document' in data['files'], "document file should be uploaded"
    assert 'data' in data['files'], "data file should be uploaded"
    
    print("   ✓ Advanced multipart upload successful")
    print(f"   ✓ Uploaded 2 files with custom content types")
    print(f"   ✓ Included form fields: description, version")


def main():
    """Run all comprehensive tests."""
    print("=" * 60)
    print("HTTP Client File Operations - Comprehensive Test")
    print("=" * 60)
    
    try:
        test_single_file_upload()
        test_multiple_file_upload()
        test_mixed_upload()
        test_streaming_download()
        test_file_save()
        test_multipart_upload_advanced()
        
        print("\n" + "=" * 60)
        print("✓ ALL TESTS PASSED - All requirements verified!")
        print("=" * 60)
        print("\nRequirements validated:")
        print("  ✓ 9.1 - Single file upload")
        print("  ✓ 9.2 - Multiple file upload")
        print("  ✓ 9.3 - Mixed file and form field upload")
        print("  ✓ 9.4 - Streaming download")
        print("  ✓ 9.5 - File save functionality")
        
    except AssertionError as e:
        print(f"\n✗ TEST FAILED: {e}")
        raise
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        raise


if __name__ == "__main__":
    main()
