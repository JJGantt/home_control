from loguru import logger
import sys
import functools
        
logger.remove()  
logger.add(
    sys.stdout,  
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level}</level> | <cyan>{module}</cyan> | <level>{message}</level>",
    level="DEBUG"
)
logger.add(
    "logs/home_control.log", 
    rotation="10 MB",  
    retention="7 days",  
    compression="zip",  
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {module} | {message}",
    level="DEBUG"
)

def debug_function_logger(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        logger.debug(f"Calling {func.__name__} with args: {args}, kwargs: {kwargs}")
        result = func(*args, **kwargs)
        logger.debug(f"{func.__name__} returned {result}")
        return result
    return wrapper

        
                     
        
