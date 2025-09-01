class LLMFailedError(Exception):
    """
    Custom exception raised when all LLM providers fail to process a request.
    
    This exception is used to distinguish between general errors and specific
    LLM service failures, allowing for better error handling and fallback mechanisms.
    
    Attributes:
        message (str): Human-readable error message
        original_exception (Exception, optional): The original exception that caused this error
    """
    
    def __init__(self, message: str, original_exception: Exception = None):
        """
        Initialize the LLMFailedError.
        
        Args:
            message (str): Descriptive error message
            original_exception (Exception, optional): Original exception for debugging
        """
        self.message = message
        self.original_exception = original_exception
        super().__init__(self.message)
    
    def __str__(self):
        """Return string representation of the error."""
        if self.original_exception:
            return f"LLMFailedError: {self.message} (Caused by: {type(self.original_exception).__name__}: {str(self.original_exception)})"
        return f"LLMFailedError: {self.message}"
    
    def get_original_exception(self) -> Exception:
        """Get the original exception that triggered this error."""
        return self.original_exception