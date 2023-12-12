from dotenv import load_dotenv
load_dotenv()

import json
from e2b import Sandbox
from openai import OpenAI

from s3_filesystem.functions import (
    FAKE_BUCKET_ROOT,
    functions_shema,
    read_file,
    write_file,
    list_dir,
)
from s3_filesystem.system_prompt import system_prompt


sbx = Sandbox()
client = OpenAI()

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
        content = read_file(sbx, path)
        print("\t", content)
      case "write_file":
        path = parsed_args["path"]
        content = parsed_args["content"]
        write_file(sbx, path, content)
      case "list_dir":
        path = parsed_args["path"]
        content = list_dir(sbx, path)
        print("\t", content)
  else:
    print(message.content)

def main():
  prompt = system_prompt([], FAKE_BUCKET_ROOT)
  response = client.chat.completions.create(
    model="gpt-4-1106-preview",
    messages=[
        {"role": "system", "content": prompt},
        # {"role": "user", "content": "Write hello world to the file in /home/user/dir2/dir3 directory"},
        {"role": "user", "content": "List content of /home/user/mnt/dir2 directory"},
    ],
    functions=functions_shema,
  )
  parse_gpt_response(response)

  sbx.close()