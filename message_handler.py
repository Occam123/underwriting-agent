from model.messageQueue.MessageQueue import Message

def handler(msg: Message) -> None:
    print(f"[Agent] {msg.content}")