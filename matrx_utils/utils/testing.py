"""
Utility functions for testing, including cleanup of async resources.
"""
import asyncio
import gc
import warnings


def cleanup_async_resources():
    """
    Clean up any lingering async resources after tests.
    
    This function:
    - Forces garbage collection to close abandoned resources
    - Closes any remaining event loops
    - Suppresses ResourceWarnings during cleanup
    
    Call this at the end of your test's if __name__ == "__main__" block.
    
    Example:
        if __name__ == "__main__":
            # ... your test code ...
            cleanup_async_resources()
    """
    # Suppress ResourceWarnings during cleanup
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", category=ResourceWarning)
        
        # Force garbage collection to clean up any unreferenced objects
        # This will trigger __del__ methods that close connections
        gc.collect()
        
        # Get all event loops that might be lingering
        try:
            # Try to get the current event loop
            loop = asyncio.get_event_loop()
            if loop and not loop.is_closed():
                # Close any pending tasks
                pending = asyncio.all_tasks(loop)
                for task in pending:
                    task.cancel()
                
                # Run the loop briefly to let cancellations process
                if pending:
                    loop.run_until_complete(asyncio.gather(*pending, return_exceptions=True))
                
                # Close the loop
                loop.close()
        except RuntimeError:
            # No event loop, which is fine
            pass
        
        # Final garbage collection pass
        gc.collect()


def async_test_wrapper(async_test_func, *args, **kwargs):
    """
    Wrapper for async test functions that ensures proper cleanup.
    
    Args:
        async_test_func: The async function to run
        *args: Arguments to pass to the function
        **kwargs: Keyword arguments to pass to the function
    
    Returns:
        The result of the async function
    
    Example:
        if __name__ == "__main__":
            result = async_test_wrapper(test_autonomous_execution, settings, handler)
    """
    try:
        result = asyncio.run(async_test_func(*args, **kwargs))
        return result
    finally:
        cleanup_async_resources()

