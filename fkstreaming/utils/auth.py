import random 
from flask import request
from functools import wraps

sessions = []

def token_required(r):
    @wraps(r)
    def decorator(*args, **kwargs):
        if token:=request.cookies.get('userToken'):
            if token not in sessions:
                user_token = None
            else:
                user_token = token
        else:
            user_token = None
        return r(user_token, *args, **kwargs)

    return decorator

def generate_token():
    return str(random.getrandbits(555))

def register_token(token):
    sessions.append(token)