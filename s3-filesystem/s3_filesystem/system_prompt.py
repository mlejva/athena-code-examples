def system_prompt(s3_bucket_content, fake_bucket_root):
  # TODO: Distinguish between files and dirs
  initial_content = "\n".join(s3_bucket_content)

  prompt=f"""You have access to a safe cloud computer.
There, you can use filesystem (read, write, list), terminal (run any command), run python code, and you're connected to the internet.

Your home directory is the `{fake_bucket_root}` directory. Always specify the full path to the file or directory you want to work with.

The initial content of the `{fake_bucket_root}` directory is:\n{initial_content}"""
  return prompt