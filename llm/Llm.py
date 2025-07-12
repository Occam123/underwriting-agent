from abc import ABC, abstractmethod


class Llm(ABC):
    @abstractmethod
    def chat(self, message: str, **kwargs):
        """
        Generate a chat response based on the provided messages.

        :param messages: List of messages to generate a response for.
        :param kwargs: Additional parameters for the chat generation.
        :return: The generated response.
        """
        raise NotImplementedError(
            "This method should be overridden by subclasses.")
