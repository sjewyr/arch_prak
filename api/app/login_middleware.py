

import datetime
from fastapi import HTTPException, Request
from api.infra.token.tokenizer import decode_token

def login_middleware(request:Request):
    try:
        cookie = request.cookies.get('access_token')
        if not cookie:
            raise HTTPException(401, "Unauthorized")
        
        res = decode_token(cookie.encode())

        t = datetime.datetime.fromisoformat(res["valid_thru"])
        if t < datetime.datetime.now():
            raise HTTPException(401, "Token expired")
        
    except ChildProcessError:
        raise HTTPException(401, "Unauthorized")