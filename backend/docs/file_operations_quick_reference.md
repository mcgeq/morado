# HTTP Client File Operations - Quick Reference

## Upload Files

### Single File
```python
client.upload_file(
    url="/upload",
    file_path="/path/to/file.pdf",
    file_field_name="document",
    additional_fields={"title": "My Doc"}
)
```

### Multiple Files
```python
client.upload_files(
    url="/upload",
    files={
        "doc": "/path/to/doc.pdf",
        "img": "/path/to/img.png"
    },
    additional_fields={"category": "reports"}
)
```

### Advanced (with content type)
```python
with open("/path/to/file.pdf", "rb") as f:
    client.upload_multipart(
        url="/upload",
        files={
            "document": ("report.pdf", f, "application/pdf")
        },
        data={"title": "Report"}
    )
```

## Download Files

### Simple Download
```python
response = client.get("/download/file.zip")
response.save_to_file("file.zip")
```

### Streaming Download
```python
response = client.get("/download/large-file.zip")
bytes_written = response.stream_to_file("large-file.zip")
print(f"Downloaded {bytes_written} bytes")
```

### Manual Streaming
```python
response = client.get("/download/file.zip")
with open("file.zip", "wb") as f:
    for chunk in response.iter_content(chunk_size=8192):
        if chunk:
            f.write(chunk)
```

## Common Patterns

### Upload with Error Handling
```python
try:
    response = client.upload_file(
        "/upload",
        "/path/to/file.pdf"
    )
    if response.is_success():
        print("Upload successful!")
except FileNotFoundError:
    print("File not found")
except Exception as e:
    print(f"Upload failed: {e}")
```

### Download with Progress
```python
response = client.get("/download/large-file.zip")
total_bytes = 0
with open("large-file.zip", "wb") as f:
    for chunk in response.iter_content(chunk_size=8192):
        if chunk:
            f.write(chunk)
            total_bytes += len(chunk)
            print(f"Downloaded: {total_bytes} bytes", end="\r")
```

### Batch Upload
```python
files_to_upload = {
    f"file{i}": f"/path/to/file{i}.txt"
    for i in range(10)
}

response = client.upload_files(
    "/batch-upload",
    files=files_to_upload
)
```
