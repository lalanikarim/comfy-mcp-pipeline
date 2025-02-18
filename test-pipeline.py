from typing import List, Union, Generator, Iterator
from base64 import b64encode
from urllib.request import urlopen


class Pipeline:
    def __init__(self):
        self.name = "Large File Test"
        pass

    async def on_startup(self):
        print(f"on_startup:{__name__}")
        pass

    async def on_shutdown(self):
        print(f"on_shutdown:{__name__}")
        pass

    async def inlet(self, body: dict, user: dict) -> dict:
        print(f"inlet:{__name__}")
        return body

    async def outlet(self, body: dict, user: dict) -> dict:
        print(f"outlet:{__name__}")
        messages = body["messages"]
        last_message = messages[-1]
        if (last_message["role"] == "assistant"
                and last_message["content"][:5] == "data:"):
            print("switching content to file")
            image_url = last_message["content"]
            content = messages[-2]["content"]
            last_message["content"] = f"Generated: {content}"
            last_message["files"] = [{"type": "image", "url": image_url}]
            messages[-1] = last_message
            body["messages"] = messages
        else:
            print("skipping outlet transformation")

        return body

    def pipe(
        self, user_message: str, model_id: str, messages: List[dict], body: dict
    ) -> Union[str, Generator, Iterator]:
        print(f"pipe:{__name__}")

        file = f"https://raw.githubusercontent.com/lalanikarim/comfy-mcp-pipeline/refs/heads/large-file-issue/assets/Image-{user_message}.png" if user_message in [
            '208', '512', '1024'] else None
        if file is not None:
            print(file)
            with urlopen(file) as image:
                encoded = b64encode(image.read()).decode("utf-8")
                return f"data:image/png;base64,{encoded}"

        return f"{__name__} response to: {user_message}"
