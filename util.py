from functools import wraps
import traceback

def backtrace(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except:
            print traceback.format_exc()
    return wrapper
