from functools import wraps
import traceback

def backtrace(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception, ex:
            print traceback.format_exc()
            raise ex
    return wrapper
