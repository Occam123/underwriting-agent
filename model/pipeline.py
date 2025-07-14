import asyncio
from typing import Callable, Any, Dict, List, Optional, Union, Awaitable
from helpers import json_dump
from model.messageQueue.MessageQueue import MessageQueue, Message

# ==== Node Graph Classes ====

class StopExecution(Exception):
    def __init__(self, message: str = None, context: dict = None):
        super().__init__(message)
        self.message = message
        self.context = context

class Node:
    async def execute(self, ctx: Dict[str, Any]) -> Dict[str, Any]:
        raise NotImplementedError

log_step = False

def is_awaitable(obj):
    return asyncio.iscoroutine(obj) or isinstance(obj, Awaitable)

class Step(Node):
    def __init__(
        self,
        id: str,
        name: str,
        function: Callable[[Dict[str, Any]], Union[Dict[str, Any], Awaitable[Dict[str, Any]]]],
        start_message: Optional[Callable[[Dict[str, Any]], str]] = None,
        end_message:   Optional[Callable[[Dict[str, Any]], str]] = None,
        message_queue: Optional[MessageQueue] = None
    ):
        self.id = id
        self.name = name
        self.function = function
        self.start_message = start_message
        self.end_message = end_message
        self.mq = message_queue

    async def execute(self, ctx):
        if log_step:
            print(f"[Step] Starting: {self.name}")
        if self.start_message:
            msg = self.start_message(ctx)
            if self.mq:
                self.mq.push(Message(msg))
        # Call function (may be sync or async)
        res = self.function(ctx)
        if is_awaitable(res):
            res = await res
        if self.end_message:
            msg = self.end_message(res, ctx)
            if self.mq:
                self.mq.push(Message(msg))
        if log_step:
            print(f"[Step] Finished: {self.name}")
        return {**ctx, self.id: res}

class Sequence(Node):
    def __init__(self, children: List[Node]):
        self.children = children

    async def execute(self, ctx):
        if log_step:
            print(f"[Sequence] Executing {len(self.children)} steps...")
        for i, child in enumerate(self.children):
            if log_step:
                print(
                    f"[Sequence] Step {i+1}/{len(self.children)}: {getattr(child, 'name', child.__class__.__name__)}")
            ctx = await child.execute(ctx)
        if log_step:
            print(f"[Sequence] Done.")
        return ctx

class AbortIf(Node):
    def __init__(
        self,
        cond: Callable[[Dict[str, Any]], bool],
        message: Union[str, Callable[[Dict[str, Any]], str]],
    ):
        self.cond = cond
        self.message = message

    async def execute(self, ctx: Dict[str, Any]) -> Dict[str, Any]:
        if log_step:
            print(f"[AbortIf] Evaluating abort condition...")
        # cond can be sync or async
        cond_result = self.cond(ctx)
        if is_awaitable(cond_result):
            cond_result = await cond_result
        if cond_result:
            msg = self.message(ctx) if callable(self.message) else self.message
            if log_step:
                print(f"[AbortIf] Condition failed: {msg}")
            raise StopExecution(msg, ctx)
        if log_step:
            print(f"[AbortIf] Condition passed.")
        return ctx

class InspectNode(Node):
    async def execute(self, ctx):
        print(json_dump(ctx))
        return ctx
