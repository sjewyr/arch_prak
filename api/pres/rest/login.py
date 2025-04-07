import datetime
import json
from fastapi import APIRouter, Form, Request, Response
from fastapi.responses import JSONResponse
from api.infra.token.tokenizer import encode_token
from starlette import status

login_router = APIRouter()


@login_router.post("/login")
def login(request: Request, response: Response, login=Form(), password=Form()):
    # Вообще надо как то чето авторизация нет да но вроде как пофигу чи да чи нет?
    with open("credls.json", "r") as f:
        credls = json.load(f)
        if login == credls.get("login") and password == credls.get("password"):
            token = encode_token(
                valid_thru=datetime.datetime.now()
                + datetime.timedelta(minutes=request.app.state.config.valid)
            )
            response.set_cookie("access_token", token)
            return "Success"
        return JSONResponse("Invalid credentials", status.HTTP_401_UNAUTHORIZED)


@login_router.post("/logout")
def logout(response: Response):
    response.set_cookie("access_token", "")
    return JSONResponse(status_code=status.HTTP_204_NO_CONTENT)
