import json
import os
import subprocess
import sys
from pathlib import Path

from dotenv import load_dotenv
from openai import AssistantEventHandler, OpenAI
from typing_extensions import override


def bold(text: str) -> str:
    return f"\033[1m{text}\033[0m"


class Ottobot:
    def __init__(self, live_mode: bool = False):
        self.live_mode = live_mode

    def _run(self, cmd: list) -> str:
        return subprocess.check_output(cmd).decode("utf-8")

    def ls(self, path: str) -> str:
        return self._run(["ls", path])

    def tree(self, path: str) -> str:
        return self._run(["tree", path, "--gitignore", "-i", "-f"])

    def cat(self, file: str) -> str:
        return self._run(["cat", file])

    def grep(self, pattern: str, path: str, recursive: bool) -> str:
        if recursive:
            result = subprocess.run(
                ["git", "grep", "-r", pattern, path], capture_output=True
            )
        else:
            result = subprocess.run(["git", "grep", pattern, path], capture_output=True)
        if result.returncode == 0:
            return result.stdout.decode("utf-8")
        else:
            return result.stderr.decode("utf-8")


class EventHandler(AssistantEventHandler):
    def __init__(self, otto):
        self.otto = otto
        super().__init__()

    @override
    def on_event(self, event):
        # Retrieve events that are denoted with 'requires_action'
        # since these will have our tool_calls
        if event.event == "thread.run.requires_action":
            run_id = event.data.id  # Retrieve the run ID from the event data
            self.handle_requires_action(event.data, run_id)

    def handle_requires_action(self, data, run_id):
        tool_outputs = []

        for tool in data.required_action.submit_tool_outputs.tool_calls:
            otto_func = getattr(self.otto, tool.function.name)
            kwargs = json.loads(tool.function.arguments)
            print(bold(f"Running tool: {tool.function.name} with arguments: {kwargs}"))
            tool_outputs.append(
                {"tool_call_id": tool.id, "output": otto_func(**kwargs)}
            )

        # Submit all tool_outputs at the same time
        self.submit_tool_outputs(tool_outputs, run_id)

    def submit_tool_outputs(self, tool_outputs, run_id):
        # Use the submit_tool_outputs_stream helper
        with client.beta.threads.runs.submit_tool_outputs_stream(
            thread_id=self.current_run.thread_id,
            run_id=self.current_run.id,
            tool_outputs=tool_outputs,
            event_handler=EventHandler(self.otto),
        ) as stream:
            for text in stream.text_deltas:
                print(text, end="", flush=True)
            print()


if __name__ == "__main__":
    load_dotenv()
    otto = Ottobot(live_mode="--live" in sys.argv)
    client = OpenAI()

    instructions = Path("instructions.txt").read_text()

    repo_root = (
        subprocess.check_output(["git", "rev-parse", "--show-toplevel"])
        .strip()
        .decode("utf-8")
    )
    print(bold(f"Starting Otto in {repo_root}"))

    os.chdir(repo_root)  # Move to the repo root so everything runs from there

    assistant = client.beta.assistants.create(
        instructions=instructions,
        model="gpt-4o",  # try mini?
        tools=[
            {
                "type": "function",
                "function": {
                    "name": "ls",
                    "description": "List files in a directory",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "path": {
                                "type": "string",
                                "description": "The path to the directory to list",
                            }
                        },
                        "required": ["path"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "tree",
                    "description": "List files in a directory in a tree format",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "path": {
                                "type": "string",
                                "description": "The path to the directory to list",
                            }
                        },
                        "required": ["path"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "cat",
                    "description": "Print the contents of a file",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "file": {
                                "type": "string",
                                "description": "The path to the file to print",
                            }
                        },
                        "required": ["file"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "grep",
                    "description": "Search for a pattern in a file",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "pattern": {
                                "type": "string",
                                "description": "The pattern to search for",
                            },
                            "path": {
                                "type": "string",
                                "description": "The path to search in",
                            },
                            "recursive": {
                                "type": "boolean",
                                "description": "Whether to search recursively",
                            },
                        },
                        "required": ["pattern", "path", "recursive"],
                    },
                },
            },
            # {
            #   "type": "function",
            #   "function": {
            #     "name": "find",
            #     "description": "Search for a file in a directory",
            #     "parameters": {
            #       "type": "object",
            #       "properties": {
            #         "name": {
            #           "type": "string",
            #           "description": "The name of the file to search for"
            #         },
            #         "path": {
            #           "type": "string",
            #           "description": "The path to the directory to search in"
            #         }
            #       },
            #       "required": ["name", "path"]
            #     }
            #   }
            # },
            # {
            #   "type": "function",
            #   "function": {
            #     "name": "patch",
            #     "description": "Generate a git patch for a file",
            #     "parameters": {
            #       "type": "object",
            #       "properties": {
            #         "file": {
            #           "type": "string",
            #           "
        ],
    )

    # Give it the initial information to work from, so it doesn't have to ask for it
    files = otto.tree(".")
    todos = otto.grep("TODO", ".", recursive=True)

    thread = client.beta.threads.create()
    message = client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=f"Current files in the repo (from `tree`):\n{files}\n\nCurrent TODOs in the repo (from `grep`):\n{todos}",
    )

    with client.beta.threads.runs.stream(
        thread_id=thread.id, assistant_id=assistant.id, event_handler=EventHandler(otto)
    ) as stream:
        stream.until_done()
