from model.messageQueue.MessageQueue import Message
from model.Log import Log, LogType
from service.LogService import log_service

async def handler(msg: Message) -> None:
    print(f"[Agent] {msg.content}")
    await log_service.log_event(log_type=LogType.INFO, content=msg.content)