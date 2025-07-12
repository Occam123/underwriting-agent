from typing import Optional

class CustomException(Exception):
    def __init__(self, message: Optional[str] = None):
        self.message = message
        super().__init__(message)

class StopExecution(Exception):
    """
    Exception to signal that the pipeline should stop executing further steps.
    Optionally carries a message and a context (such as the last result).
    """
    def __init__(self, message: str = None, context: dict = None):
        super().__init__(message)
        self.message = message
        self.context = context

class AgentContext(CustomException):pass
class DocumentProcessorException(CustomException):pass
class AzureDocIntelException(CustomException): pass
class MistralDocIntelException(CustomException): pass