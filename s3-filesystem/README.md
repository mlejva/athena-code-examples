# Using S3 bucket in Sandbox

The main idea is to use the S3 pre-signed URLs.

- We let the LLM think that there's for example a `/mnt/s3` directory (through system prompt for example)
- If the LLM is trying to read or write a file in the `/mnt/s3` directory, we intercept the call and we use the pre-signed S3 URL to read or write the file
- All other calls are passed to the real filesystem


Later (~3 weeks), we'll add a way to connect S3 bucket to the filesytem, but for now, we'll use pre-signed URLs.