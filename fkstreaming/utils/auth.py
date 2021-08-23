import random 
from flask import request, make_response, redirect, url_for
from fkstreaming.api.errors import AuthenticationError
from functools import wraps

class Authentication:
    def __init__(self):
        self.sessions = []
       
    def token_required(self, r):
        @wraps(r)
        def decorator(*args, **kwargs):
            if token:=request.cookies.get('userToken'):
                if token not in self.sessions:
                    return redirect(url_for('home./'))
            else:
                return redirect(url_for('home./'))
            return r(*args, **kwargs)
            
        return decorator
        
    def generate_token(self):
        return str(random.getrandbits(555))

    def register_token(self, token):
        self.sessions.append(token)
    
    def get_current_token(self):
        return request.cookies.get('userToken')
        
    def login(self, resp : request):
        resp = make_response(resp)
        new_token = self.generate_token()
        self.register_token(new_token)
        resp.set_cookie('userToken', new_token)
        return resp

if __name__ == '__main__':
    pass 
else:
    Auth = Authentication()