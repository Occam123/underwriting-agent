from typing import Callable, Any, Dict, List, Optional
from model.messageQueue.MessageQueue import MessageQueue, Message

# ==== Node Graph Classes ====


class StopExecution(Exception):
    """
    Exception to signal that the pipeline should stop executing further steps.
    Optionally carries a message and a context (such as the last result).
    """

    def __init__(self, message: str = None, context: dict = None):
        super().__init__(message)
        self.message = message
        self.context = context


class Node:
    def execute(self, ctx: Dict[str, Any]) -> Dict[str, Any]:
        raise NotImplementedError


class Step(Node):
    def __init__(
        self,
        id: str,
        name: str,
        function: Callable[[Dict[str, Any]], Dict[str, Any]],
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

    def execute(self, ctx):
        # print(f"[Step] Starting: {self.name}")
        if self.start_message:
            msg = self.start_message(ctx)
            if self.mq:
                self.mq.push(Message(msg))
        res = self.function(ctx)
        if self.end_message:
            msg = self.end_message(res)
            if self.mq:
                self.mq.push(Message(msg))
        # print(f"[Step] Finished: {self.name}")
        return {**ctx, self.id: res}


class Sequence(Node):
    def __init__(self, children: List[Node]):
        self.children = children

    def execute(self, ctx):
        # print(f"[Sequence] Executing {len(self.children)} steps...")
        for i, child in enumerate(self.children):
            # print(
            #     f"[Sequence] Step {i+1}/{len(self.children)}: {getattr(child, 'name', child.__class__.__name__)}")
            ctx = child.execute(ctx)
        # print(f"[Sequence] Done.")
        return ctx


class AbortIf(Node):
    def __init__(self, cond: Callable[[Dict[str, Any]], bool], message: str):
        self.cond = cond
        self.message = message

    def execute(self, ctx):
        # print(f"[AbortIf] Evaluating abort condition...")
        if not self.cond(ctx):
            # print(f"[AbortIf] Condition failed: {self.message}")
            raise StopExecution(self.message, ctx)
        # print(f"[AbortIf] Condition passed.")
        return ctx
