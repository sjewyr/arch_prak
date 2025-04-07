import datetime
import jwt


def encode_token(valid_thru: datetime.datetime):
    toks = jwt.encode({"valid_thru": valid_thru.isoformat()}, key="SECRET")
    return toks


def decode_token(token: bytes):
    res = jwt.decode(token, key="SECRET", algorithms=["HS256"])
    return res
