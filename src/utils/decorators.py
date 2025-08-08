"""
Common decorators for Meeting Agent
Provides reusable error handling, logging, and performance decorators.
"""

import functools
import time
from typing import Any, Callable, Optional, Union

from .logger import setup_logger

logger = setup_logger(__name__)


def handle_errors(
    default_return: Any = None,
    log_errors: bool = True,
    error_message: Optional[str] = None,
    raise_on_error: bool = False
):
    """
    Decorator for consistent error handling
    
    Args:
        default_return: Value to return on error
        log_errors: Whether to log errors
        error_message: Custom error message prefix
        raise_on_error: Whether to re-raise exceptions
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                if log_errors:
                    message = error_message or f"Error in {func.__name__}"
                    logger.error(f"{message}: {e}")
                
                if raise_on_error:
                    raise
                
                return default_return
        return wrapper
    return decorator


def handle_api_errors(default_return: Any = None):
    """
    Decorator specifically for API calls that may fail
    
    Args:
        default_return: Value to return on API error
    """
    return handle_errors(
        default_return=default_return,
        log_errors=True,
        error_message="API call failed"
    )


def handle_db_errors(default_return: Any = None):
    """
    Decorator for database operations that may fail
    
    Args:
        default_return: Value to return on database error
    """
    return handle_errors(
        default_return=default_return,
        log_errors=True,
        error_message="Database operation failed"
    )


def handle_file_errors(default_return: Any = None):
    """
    Decorator for file operations that may fail
    
    Args:
        default_return: Value to return on file error
    """
    return handle_errors(
        default_return=default_return,
        log_errors=True,
        error_message="File operation failed"
    )


def performance_monitor(log_threshold_ms: float = 1000.0):
    """
    Decorator to monitor function performance
    
    Args:
        log_threshold_ms: Log warning if function takes longer than this (milliseconds)
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                duration_ms = (time.time() - start_time) * 1000
                
                if duration_ms > log_threshold_ms:
                    logger.warning(f"{func.__name__} took {duration_ms:.2f}ms (threshold: {log_threshold_ms}ms)")
                else:
                    logger.debug(f"{func.__name__} completed in {duration_ms:.2f}ms")
                
                return result
            except Exception as e:
                duration_ms = (time.time() - start_time) * 1000
                logger.error(f"{func.__name__} failed after {duration_ms:.2f}ms: {e}")
                raise
        return wrapper
    return decorator


def retry_on_error(
    max_retries: int = 3,
    delay_seconds: float = 1.0,
    backoff_multiplier: float = 2.0,
    exceptions: tuple = (Exception,)
):
    """
    Decorator to retry function on specific exceptions
    
    Args:
        max_retries: Maximum number of retry attempts
        delay_seconds: Initial delay between retries
        backoff_multiplier: Multiply delay by this factor each retry
        exceptions: Tuple of exceptions to retry on
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            delay = delay_seconds
            
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    
                    if attempt == max_retries:
                        logger.error(f"{func.__name__} failed after {max_retries} retries: {e}")
                        break
                    
                    logger.warning(f"{func.__name__} attempt {attempt + 1} failed, retrying in {delay:.1f}s: {e}")
                    time.sleep(delay)
                    delay *= backoff_multiplier
            
            raise last_exception
        return wrapper
    return decorator


def validate_inputs(**validators):
    """
    Decorator to validate function inputs
    
    Args:
        **validators: Keyword arguments mapping parameter names to validation functions
        
    Example:
        @validate_inputs(name=lambda x: isinstance(x, str) and len(x) > 0)
        def create_meeting(name: str):
            pass
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Get function signature to map args to parameter names
            import inspect
            sig = inspect.signature(func)
            bound_args = sig.bind(*args, **kwargs)
            bound_args.apply_defaults()
            
            # Validate each specified parameter
            for param_name, validator in validators.items():
                if param_name in bound_args.arguments:
                    value = bound_args.arguments[param_name]
                    if not validator(value):
                        raise ValueError(f"Invalid value for parameter '{param_name}': {value}")
            
            return func(*args, **kwargs)
        return wrapper
    return decorator


# Common validation functions
def not_empty_string(value: Any) -> bool:
    """Validate that value is a non-empty string"""
    return isinstance(value, str) and len(value.strip()) > 0


def positive_number(value: Any) -> bool:
    """Validate that value is a positive number"""
    return isinstance(value, (int, float)) and value > 0


def non_empty_list(value: Any) -> bool:
    """Validate that value is a non-empty list"""
    return isinstance(value, list) and len(value) > 0