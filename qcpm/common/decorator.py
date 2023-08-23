from functools import wraps, partial

from qcpm.common.timer import Timer


def countDecorator(func):
    index = 0

    @wraps(func)
    def wrapper(*args, **kwargs):
        nonlocal index
        r = func(*args, index = index, **kwargs)
        index += 1

        return r
    
    return wrapper

def timerDecorator(func=None, description=''):
    if func is None:
        return partial(timerDecorator, description=description)
    
    @wraps(func)
    def wrapper(*args, **kwargs):
        with Timer(description):
            r = func(*args, **kwargs)
        
        return r
    
    return wrapper
