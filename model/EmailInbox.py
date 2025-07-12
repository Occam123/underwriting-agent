from model.Email import Email
import asyncio


class EmailInbox:

    def __init__(self, callback: callable) -> None:
        self.callback = callback
        self.queue = []

    def push(self, email: Email) -> None:
        # If callback is coroutine, run in event loop
        if asyncio.iscoroutinefunction(self.callback):
            asyncio.run(self.callback(email))
        else:
            self.callback(email)
