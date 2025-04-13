import datetime
import jwt
from fastapi import HTTPException, Request


def login_middleware(request: Request):
    try:
        cookie = request.cookies.get("access_token")
        if not cookie:
            raise HTTPException(401, "Unauthorized")

        res = decode_token(cookie.encode())

        t = datetime.datetime.fromisoformat(res["valid_thru"])
        if t < datetime.datetime.now():
            raise HTTPException(401, "Token expired")

    except ChildProcessError:
        raise HTTPException(401, "Unauthorized")
    

def encode_token(valid_thru: datetime.datetime):
    toks = jwt.encode({"valid_thru": valid_thru.isoformat()}, key="SECRET")
    return toks


def decode_token(token: bytes):
    res = jwt.decode(token, key="SECRET", algorithms=["HS256"])
    return res