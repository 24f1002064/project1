# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "fastapi",
#     "uvicorn",
#     "requests"
# ]
# ///

from fastapi import FastAPI, HTTPException
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
import os
import requests

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
tools = [
    {
        "type": "function",
        "function": {
            "name": "script_runner",
            "description": "Install a package and run a script url with provided arguments",
            "parameters": {
                "type": "object",
                "properties": {
                    "script_url": {
                        "type": "string",
                        "description": "The url of the script to run.",
                    },
                    "args": {
                        "type": "array",
                        "items": {
                            "type": "string"
                        },
                        "description": "List of arguments to pass to the script.",
                    },
                    "required": ["script_url", "args"],
                },
            },
        },
    }
]
AIPROXY_TOKEN = os.getenv("AIPROXY_TOKEN")


@app.get("/")
def read_file():
    return {"Hello": "World"}


@app.get("/read")
def read_file(pth: str):
    try:
        with open(pth, "r") as file:
            content = file.read()
        return {"content": content}
    except Exception as e:
        raise HTTPException(status_code=404, detail="File doesn't exists")


@app.post("/run")
def task_runner(task: str):
    url = "https://aiproxy.sanand.workers.dev/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {AIPROXY_TOKEN}"}
    data = {
        "model": "gpt-40-mini",
        "messages": [
            {"role": "user", "content": task},
            {
                "role": "system",
                "content": """ 
                You are an assistant who has to do variety of tasks. If your task involves running a script, you can use the script_runner tool.
             If your task involves writing a code, you can use the task_runner tool.
""",
            },
        ],
        "tools": tools,
        "tools:choice": "auto"
    }

    response = requests.post(url, headers=headers, json=data)

    if response.status_code == 200:
        return response.json()
    else:
        raise HTTPException(
            status_code=response.status_code, detail="Task execution failed"
        )


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
