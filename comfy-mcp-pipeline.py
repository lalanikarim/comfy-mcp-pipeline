from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from pydantic import BaseModel
from typing import Generator, Iterator, Union, List
import asyncio

import os


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
                "COMFY_WORKFLOW_JSON_FILE": os.getenv("COMFY_WORKFLOW_JSON_FILE", "path-to-workflow-json-file"),
                "PROMPT_NODE_ID": os.getenv("PROMPT_NODE_ID", "prompt-node-id"),
                "OUTPUT_NODE_ID": os.getenv("OUTPUT_NODE_ID", "output-node-id"),
            }
        )
        self.read_stream = None
        self.write_stream = None
        self.session: ClientSession = None
        pass

    async def on_startup(self):
        print(f"on_startup:{__name__}")
        server_params = StdioServerParameters(
            command="uvx",
            args=["comfy-mcp-server"],
            env=os.environ
        )
        (self.read_stream, self.write_stream) = await stdio_client(server_params)
        self.session = await ClientSession(self.read_stream, self.write_stream)
        await self.session.initialize()
        pass

    async def on_shutdown(self):
        print(f"on_shutdown:{__name__}")
        await self.session.__aexit__()
        self.write_stream.close()
        self.read_stream.close()
        pass

    def pipe(
        self, user_message: str, model_id: str, messages: List[dict], body: dict
    ) -> Union[str, Generator, Iterator]:
        async def apipe(
            user_message: str, model_id: str, messages: List[dict], body: dict
        ) -> Union[str, Generator, Iterator]:
            return await self.session.call_tool("generate_image", arguments={
                "prompt": user_message
            })
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(self.apipe(user_message, model_id, messages, body))
