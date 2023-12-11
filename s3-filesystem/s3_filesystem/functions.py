functions = [
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