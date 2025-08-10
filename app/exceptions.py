class ToolError(Exception):
    """Raised when a tool encounters an error."""

    def __init__(self, message):
        self.message = message


class CodingAgentError(Exception):
    """Base exception for all CodingAgent errors"""


class TokenLimitExceeded(CodingAgentError):
    """Exception raised when the token limit is exceeded"""


class LlmError(Exception):
    """Exception raised when there is an error with the LLM"""


class LlmCriticalError(Exception):
    """Exception raised for critical errors in LLM operations"""

    def __init__(self, message):
        super().__init__(message)
        self.message = message
