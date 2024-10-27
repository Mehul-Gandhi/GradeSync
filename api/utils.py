import csv
import io
from fastapi import HTTPException
from functools import wraps
from requests.exceptions import RequestException

def csv_to_json(csv_content: str):
    """
    Converts CSV content to a JSON-like list of dictionaries.
    
    Parameters:
        csv_content (str): The raw CSV content as a string.

    Returns:
        list: A list of dictionaries representing the CSV data.
    """
    csv_reader = csv.DictReader(io.StringIO(csv_content))
    return [row for row in csv_reader]

def handle_errors(func):
    """
    Decorator to handle common exceptions in API endpoints.

    This decorator wraps an API endpoint function to provide standardized error handling. 
    It catches specific exceptions, such as client-side errors (e.g., `ValueError`, `TypeError`, `AttributeError`) 
    and network-related errors (`RequestException`), and returns appropriate HTTP responses with 
    meaningful error messages. If an unexpected error occurs, it returns a 500 Internal Server Error.

    Parameters:
        func (function): The API endpoint function to be wrapped by the decorator.

    Returns:
        function: A wrapper function that executes the original function with error handling applied.

    Raises:
        HTTPException: If a known error occurs, an appropriate `HTTPException` is raised with
                       status codes:
                       - 400 for client-side errors
                       - 503 for network-related errors
                       - 500 for unexpected errors

    Example:
        >>> @app.get("/example")
        >>> @handle_errors
        >>> async def example_endpoint():
        >>>     # Your endpoint logic here

    Usage:
        Apply this decorator to any FastAPI endpoint to handle errors consistently, without needing
        to duplicate error-handling logic across multiple endpoints.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            # Execute the wrapped function
            return func(*args, **kwargs)
        
        except (ValueError, TypeError, AttributeError) as e:
            # Handle client-side errors (400-level)
            print(f"Client-side error: {e}")
            raise HTTPException(status_code=400, detail="Invalid request: missing or incorrect parameters.")
        
        except RequestException as e:
            # Handle network-related errors (503-level)
            print(f"Network error: {e}")
            raise HTTPException(status_code=503, detail="Service unavailable: network error while connecting to Gradescope.")
        
        except Exception as e:
            # Handle all other unexpected server-side errors (500-level)
            print(f"Unexpected server error: {e}")
            raise HTTPException(status_code=500, detail="An unexpected server error occurred.")
    return wrapper
