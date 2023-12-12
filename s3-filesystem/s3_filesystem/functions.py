import s3_filesystem.bucket as bucket

FAKE_BUCKET_ROOT = "/home/user/mnt"

functions_shema = [
  {
      "name": "read_file",
      "description": "Reads file from filesystem",
      "parameters": {
          "type": "object",
          "properties": {
              "path": {
                  "type": "string",
                  "description": "Path to file",
              },
          },
          "required": ["path"],
      },
  },
  {
      "name": "list_dir",
      "description": "List content of directory",
      "parameters": {
          "type": "object",
          "properties": {
              "path": {
                  "type": "string",
                  "description": "Path to directory",
              },
          },
          "required": ["path"],
      },
  },
  {
      "name": "write_file",
      "description": "Write content to a file in filesystem. If file exists, it will be overwritten.",
      "parameters": {
          "type": "object",
          "properties": {
              "path": {
                  "type": "string",
                  "description": "Path to file",
              },
              "content": {
                  "type": "string",
                  "description": "Content of a file",
              },
          },
          "required": ["path"],
      },
  },
]

def read_file(sbx, path):
  if FAKE_BUCKET_ROOT in path:
    bucket_path = path.split(FAKE_BUCKET_ROOT, 1)[1]
    print("Read file from S3 bucket", bucket_path)
    return bucket.read_file(bucket_path)
  else:
    return sbx.filesystem.read(path)

def write_file(sbx, path, content):

  if FAKE_BUCKET_ROOT in path:
    bucket_path = path.split(FAKE_BUCKET_ROOT, 1)[1]

    # Generate a pre-signed URL to write a file to the S3 bucket
    print("Write file to S3 bucket", bucket_path)
    bucket.write_file(bucket_path, content)
  else:
    # Create directory if it doesn't exist
    base_path = path.rsplit("/", 1)[0]
    # Empty string is root - root must exist
    if base_path != "":
      sbx.filesystem.make_dir(base_path)

    # Or use sbx.filesystem.write_bytes if operating with non-text content
    # read more here https://e2b.dev/docs/sandbox/api/filesystem#write-bytes
    sbx.filesystem.write(path, content)

def list_dir(sbx, path):
  if FAKE_BUCKET_ROOT in path:
    bucket_path = path.split(FAKE_BUCKET_ROOT, 1)[1]
    print("List directory in S3 bucket", bucket_path)
    return bucket.list_dir(bucket_path)
  else:
    return [x.name for x in sbx.filesystem.list(path)]
