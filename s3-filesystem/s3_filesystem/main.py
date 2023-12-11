import json
from e2b import Sandbox
from dotenv import load_dotenv
from openai import OpenAI

from s3_filesystem.functions import functions
from s3_filesystem.system_prompt import system_prompt

load_dotenv()

FAKE_BUCKET_ROOT = "/home/user"
sbx = Sandbox()
client = OpenAI()

def read_file(path):
  if FAKE_BUCKET_ROOT in path:
    bucket_path = path.split(FAKE_BUCKET_ROOT, 1)[1]
    # Use pre-signed URL to receive a file from the S3 bucket
    print("[TODO] Read file from S3 bucket", path)
  else:
    return sbx.filesystem.read(path)

def list_dir(path):
  if FAKE_BUCKET_ROOT in path:
    bucket_path = path.split(FAKE_BUCKET_ROOT, 1)[1]
    # Use pre-signed URL to list directory in the S3 bucket
    print("[TODO] List directory in S3 bucket", path)
  else:
    return sbx.filesystem.list(path)

def write_file(path, content):
  if FAKE_BUCKET_ROOT in path:
    bucket_path = path.split(FAKE_BUCKET_ROOT, 1)[1]
    # Use pre-signed URL to write a file to the S# bucket
    print("[TODO] Write file to S3 bucket", path)
  else:
    # Or use sbx.filesystem.write_bytes if operating with non-text content
    # read more here https://e2b.dev/docs/sandbox/api/filesystem#write-bytes
    sbx.filesystem.write(path, content)

def parse_gpt_response(response):
  message = response.choices[0].message

  if message.function_call != None:
    func_name = message.function_call.name
    args = message.function_call.arguments
    print("[Function Call]", func_name, args)

    parsed_args = json.loads(args)
    match func_name:
      case "read_file":
        path = parsed_args["path"]
        content = read_file(path)
        print("\t", content)
      case "write_file":
        path = parsed_args["path"]
        content = parsed_args["content"]
        write_file(path, content)
      case "list_dir":
        path = parsed_args["path"]
        content = list_dir(path)
        print("\t", content)
  else:
    print(message.content)

def main():
  prompt = system_prompt("", FAKE_BUCKET_ROOT)
  response = client.chat.completions.create(
    model="gpt-4-1106-preview",
    messages=[
        {"role": "system", "content": prompt},
        {"role": "user", "content": "Write hello world to a file"},
        # {"role": "assistant", "content": '{"content": "hello world"}', "path":"/home/user/hello.txt"},
        # {"role": "user", "content": "List files of a directory"},
    ],
    functions=functions,
  )
  parse_gpt_response(response)

  sbx.close()