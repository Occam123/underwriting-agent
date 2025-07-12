from typing import List, Optional, Union, Any
from enum import Enum
from openai import OpenAI
import base64

from llm.Llm import Llm
from config.Config import config
from openai.types.responses.response_output_message import ResponseOutputMessage

class OpenAi(Llm):
    def __init__(self) -> None:
        self.client = OpenAI(api_key=config.OPENAI.API_KEY)

    def chat(
        self,
        message: str,
        system_message: Optional[str] = None,
        files: Optional[List[dict]] = None,
        response_format: Any = None,
        tools: List[dict] = [],
        model: str = "gpt-4o",
    ) -> Union[ResponseOutputMessage, str, Any]:
        # Helper to dispatch Pydantic parse
        def _use_parse(messages):
            resp = self.client.beta.chat.completions.parse(
                model=model,
                messages=messages,
                response_format=response_format,
                tools=tools if tools else [],
            )
            return resp.choices[0].message.parsed

        # Vision + structured/text
        if files:
            content = [{"type": "text", "text": message}]
            for f in files:
                if f["type"] == "image":
                    b64 = (base64.b64encode(f["content"]).decode("utf-8")
                           if isinstance(f["content"], bytes)
                           else f["content"])
                    mime = f.get("mime", "image/png")
                    content.append({
                        "type": "image_url",
                        "image_url": {"url": f"data:{mime};base64,{b64}"}
                    })
            messages = []
            if system_message:
                messages.append({"role": "system", "content": system_message})
            messages.append({"role": "user", "content": content})

            if response_format is not None:
                return _use_parse(messages)

            api_args = {"model": model, "messages": messages}
            if tools:
                api_args["tools"] = tools
            response = self.client.chat.completions.create(**api_args)
            return response.choices[0].message.content

        # Text-only
        else:
            messages = []
            if system_message:
                messages.append({"role": "system", "content": system_message})
            messages.append({"role": "user", "content": message})

            if response_format is not None:
                return _use_parse(messages)

            api_args = {"model": model, "messages": messages}
            if tools:
                api_args["tools"] = tools
            response = self.client.chat.completions.create(**api_args)
            return response.choices[0].message.content

class Model(str, Enum):
    gpt_4_1 = "gpt-4.1"
    gpt_4o_mini = "gpt-4o-mini"
