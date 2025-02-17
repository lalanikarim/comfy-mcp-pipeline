import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from mcp.types import ImageContent
from pydantic import BaseModel
from typing import Generator, Iterator, Union, List
import os
import subprocess
import sys


class Pipeline:
    class Valves(BaseModel):
        COMFY_URL: str
        COMFY_WORKFLOW_JSON_FILE: str
        PROMPT_NODE_ID: str
        OUTPUT_NODE_ID: str
        pass

    def __init__(self):
        self.name = "Comfy MCP Pipeline"
        self.valves = self.Valves(
            **{
                "COMFY_URL": os.getenv("COMFY_URL", "comfy-url"),
                "COMFY_WORKFLOW_JSON_FILE": os.getenv(
                    "COMFY_WORKFLOW_JSON_FILE",
                    "path-to-workflow-json-file"),
                "PROMPT_NODE_ID": os.getenv("PROMPT_NODE_ID",
                                            "prompt-node-id"),
                "OUTPUT_NODE_ID": os.getenv("OUTPUT_NODE_ID",
                                            "output-node-id"),
            }
        )
        pass

    async def on_startup(self):
        print(f"on_startup:{__name__}")
        subprocess.check_call([
            sys.executable,
            "-m",
            "pip",
            "install",
            "uv",
        ])
        pass

    async def on_shutdown(self):
        print(f"on_shutdown:{__name__}")
        pass

    def pipe(
        self, user_message: str, model_id: str,
        messages: List[dict], body: dict
    ) -> Union[str, Generator, Iterator]:
        if len(user_message) > 500:
            return ""
        print(f"Prompt: {user_message}")
        server_params = StdioServerParameters(
            command="/usr/local/bin/uvx",
            args=["comfy-mcp-server"],
            env={
                "COMFY_URL": self.valves.COMFY_URL,
                "COMFY_WORKFLOW_JSON_FILE": (
                    self.valves.COMFY_WORKFLOW_JSON_FILE
                ),
                "PROMPT_NODE_ID": self.valves.PROMPT_NODE_ID,
                "OUTPUT_NODE_ID": self.valves.OUTPUT_NODE_ID,
                "PATH": os.getenv("PATH"),
            }
        )

        async def apipe(
            user_message: str, model_id: str, messages: List[dict], body: dict
        ) -> Union[str, Generator, Iterator]:
            async with stdio_client(server_params) as (read, write):
                async with ClientSession(read, write) as session:
                    await session.initialize()
                    return await session.call_tool(
                        "generate_image", arguments={
                            "prompt": user_message
                        })
        coro = apipe(user_message, model_id, messages, body)
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            print("asyncio.run")
            result = asyncio.run(coro)
        else:
            print("loop.run_until_complete")
            result = loop.run_until_complete(coro)
        print("result ready")
        content = result.content[0]

        if isinstance(content, ImageContent):
            print("image")
            md_content = f"data:{content.mimeType};base64, {content.data}"
            return md_content
        else:
            print("text")
            print(content)
            return f"{content.text}\n"

    async def outlet(self, body: dict, user: dict) -> dict:
        print(f"outlet:{__name__}")

        messages = body["messages"]
        last_message = messages[-1]
        if (last_message["role"] == "assistant"
                and last_message["content"][:5] == "data:"):
            image_url = last_message["content"]
            content = messages[-2]["content"]
            last_message["content"] = f"Generated: {content}"
            last_message["files"] = [{"type": "image", "url": image_url}]
            messages[-1] = last_message
            body["messages"] = messages

        return body
