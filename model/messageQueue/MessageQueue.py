import threading
import asyncio
from typing import Callable, Optional

class Message:
    def __init__(self, content: str):
        self.content = content

class MessageQueue:
    def __init__(self, callback: Optional[Callable[[Message], None]] = None):
        self.queue = []
        self.callback = callback
        self._lock = threading.Lock()
        self._new_message_event = threading.Event()
        self._stop_event = threading.Event()
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._loop = asyncio.new_event_loop()
        self._thread.start()

    def push(self, message: Message) -> None:
        with self._lock:
            self.queue.append(message)
            self._new_message_event.set()

    def __iter__(self):
        return iter(self.queue)

    def __getitem__(self, index):
        return self.queue[index]

    def stop(self):
        self._stop_event.set()
        self._new_message_event.set()
        self._thread.join()

    def _run(self):
        print("Starting message queue")
        asyncio.set_event_loop(self._loop)
        while not self._stop_event.is_set():
            self._new_message_event.wait()
            self._new_message_event.clear()
            while True:
                with self._lock:
                    if not self.queue:
                        break
                    message = self.queue[-1]  # Process only the latest message
                if self.callback:
                    if asyncio.iscoroutinefunction(self.callback):
                        # If the callback is async
                        self._loop.run_until_complete(self.callback(message))
                    else:
                        # If the callback is sync
                        self.callback(message)
                break

    def set_callback(self, callback: Callable[[Message], None]):
        self.callback = callback
