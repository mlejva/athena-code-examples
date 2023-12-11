# Using S3 bucket in Sandbox

This example makes a single call to GPT-4-Turbo to make a read, write, or list operation in the filesystem.
We use function calling and manually parse the respone.

## How it works
- We let the LLM think that there's for example a `/home/user/mnt` directory (through system prompt for example)
- If the LLM is trying to read or write a file in the `/home/user/mnt` directory, we call the S3 API
- All other filesystem calls are passed to the Sandbox's filesystem


## Future
Later, we'll add an easy way to connect S3 bucket to the filesytem, something like this:
```python
sandbox = Sandbox(
  s3_bucket_name="my-bucket",
  s3_mount_path="/home/user/mnt"
)
```