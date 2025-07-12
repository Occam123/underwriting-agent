from model.messageQueue.MessageQueue import MessageQueue
from message_handler import handler

message_queue = MessageQueue(callback=handler)