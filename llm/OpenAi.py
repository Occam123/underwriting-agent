# from typing import List, Optional, Union, Any
# from enum import Enum
# from openai import OpenAI
# import base64

# from llm.Llm import Llm
# from config.Config import config
# from openai.types.responses.response_output_message import ResponseOutputMessage

# class OpenAi(Llm):
#     def __init__(self) -> None:
#         self.client = OpenAI(api_key=config.OPENAI.API_KEY)

#     def chat(
#         self,
#         message: str,
#         system_message: Optional[str] = None,
#         files: Optional[List[dict]] = None,
#         response_format: Any = None,
#         tools: List[dict] = [],
#         model: str = "gpt-4o",
#     ) -> Union[ResponseOutputMessage, str, Any]:
#         # Helper to dispatch Pydantic parse
#         def _use_parse(messages):
#             resp = self.client.beta.chat.completions.parse(
#                 model=model,
#                 messages=messages,
#                 response_format=response_format,
#                 tools=tools if tools else [],
#             )
#             return resp.choices[0].message.parsed

#         # Vision + structured/text
#         if files:
#             content = [{"type": "text", "text": message}]
#             for f in files:
#                 if f["type"] == "image":
#                     b64 = (base64.b64encode(f["content"]).decode("utf-8")
#                            if isinstance(f["content"], bytes)
#                            else f["content"])
#                     mime = f.get("mime", "image/png")
#                     content.append({
#                         "type": "image_url",
#                         "image_url": {"url": f"data:{mime};base64,{b64}"}
#                     })
#             messages = []
#             if system_message:
#                 messages.append({"role": "system", "content": system_message})
#             messages.append({"role": "user", "content": content})

#             if response_format is not None:
#                 return _use_parse(messages)

#             api_args = {"model": model, "messages": messages}
#             if tools:
#                 api_args["tools"] = tools
#             response = self.client.chat.completions.create(**api_args)
#             return response.choices[0].message.content

#         # Text-only
#         else:
#             messages = []
#             if system_message:
#                 messages.append({"role": "system", "content": system_message})
#             messages.append({"role": "user", "content": message})

#             if response_format is not None:
#                 return _use_parse(messages)

#             api_args = {"model": model, "messages": messages}
#             if tools:
#                 api_args["tools"] = tools
#             response = self.client.chat.completions.create(**api_args)
#             return response.choices[0].message.content

# class Model(str, Enum):
#     gpt_4_1 = "gpt-4.1"
#     gpt_4o_mini = "4o-mini"


from typing import List, Optional, Union, Any
from enum import Enum
from openai import OpenAI
import base64

from llm.Llm import Llm
from config.Config import config
from openai.types.responses.response_output_message import ResponseOutputMessage
from openai.types.responses.response_reasoning_item import ResponseReasoningItem


class OpenAi(Llm):
    # Models that support the Responses API for parsing or reasoning
    _REASONING_MODELS = {
        "gpt-4o", "gpt-4o-mini",
        "gpt-4.1", "gpt-4.1-mini", "gpt-4.1-nano",
        "o1", "o3", "o3-mini", "o4-mini"
    }
    # Subset that accept a reasoning.effort parameter
    _EFFORT_MODELS = {"o1", "o3-mini", "o4-mini"}

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
        reasoning: Optional[dict] = None,
        background: bool = False,
    ) -> Union[ResponseOutputMessage, str, Any]:
        # Validate reasoning parameter
        if reasoning is not None and model not in self._EFFORT_MODELS:
            raise ValueError(
                f"Model `{model}` does not support reasoning settings; "
                "remove `reasoning` or choose one of "
                f"{sorted(self._EFFORT_MODELS)}."
            )

        # Build shared message list (for both parse and raw)
        def build_messages():
            msgs = []
            if system_message:
                msgs.append({"role": "system", "content": system_message})
            msgs.append({"role": "user", "content": message})
            return msgs

        # 1) STRUCTURED PARSE (old .parse behavior)
        if response_format is not None:
            # If files are present, fall back to chat.parse
            if files:
                return self._fallback_parse(build_messages(), response_format, tools)
            # Otherwise, use Responses.parse
            parse_kwargs = {
                "model": model,
                "input": build_messages(),
                "text_format": response_format,
                "tools": tools or []
            }
            if reasoning:
                parse_kwargs["reasoning"] = reasoning
            parsed = self.client.responses.parse(**parse_kwargs)

            # If no reasoning requested, return the Pydantic result directly
            if reasoning is None:
                return parsed.output_parsed

            # If reasoning _was_ requested, extract summary + parsed
            summary = []
            for item in parsed.output:
                if isinstance(item, ResponseReasoningItem):
                    summary.extend([s.text for s in item.__dict__.get("summary", [])])
            return {
                "result": parsed.output_parsed,
                "summary": summary or None
            }

        # 2) RAW TEXT with reasoning (Responses.create)
        if reasoning is not None:
            api_args = {
                "model": model,
                "input": build_messages(),
                "tools": tools or []
            }
            if system_message:
                api_args["instructions"] = system_message
            api_args["reasoning"] = reasoning
            if background:
                api_args["background"] = True

            resp = self.client.responses.create(**api_args)

            # Extract optional summary
            summary = []
            for item in resp.output:
                if isinstance(item, ResponseReasoningItem):
                    summary.extend([s.text for s in item.__dict__.get("summary", [])])

            # Return dict only when reasoning is used
            return {
                "result": resp.output_text,
                "summary": summary or None
            }

        # 3) FALLBACK: exactly your old chat.completions flow

        # Vision + attachments
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

            # If someone ever tries structured parse here, route to parse
            if response_format is not None:
                return self._fallback_parse(messages, response_format, tools)

            api_args = {"model": model, "messages": messages}
            if tools:
                api_args["tools"] = tools
            resp = self.client.chat.completions.create(**api_args)
            return resp.choices[0].message.content

        # Plain text-only chat
        messages = build_messages()
        if response_format is not None:
            return self._fallback_parse(messages, response_format, tools)

        api_args = {"model": model, "messages": messages}
        if tools:
            api_args["tools"] = tools
        resp = self.client.chat.completions.create(**api_args)
        return resp.choices[0].message.content

    def _fallback_parse(self, messages, response_format, tools):
        """Mirror your old _use_parse helper exactly."""
        resp = self.client.beta.chat.completions.parse(
            model=messages[0].get("model"),  # or track model separately
            messages=messages,
            response_format=response_format,
            tools=tools or []
        )
        return resp.choices[0].message.parsed


class Model(str, Enum):
    gpt_4_1     = "gpt-4.1"
    gpt_4o      = "gpt-4o"
    gpt_4o_mini = "gpt-4o-mini"
    o1          = "o1"
    o3_mini     = "o3-mini"
    o4_mini     = "o4-mini"
