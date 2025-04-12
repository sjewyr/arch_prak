import datetime
import json
from fastapi import APIRouter, Form, Request, Response
from fastapi.responses import JSONResponse
from login_utils import encode_token
from starlette import status


router = APIRouter()


@router.post("/login")
def login(request: Request, response: Response, login=Form(), password=Form()):
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


@router.post("/logout")
def logout(response: Response):
    response.set_cookie("access_token", "")
    return JSONResponse(status_code=status.HTTP_204_NO_CONTENT)



@router.get("/first")
def lab1(
    date_start: datetime.date,
    date_end: datetime.date,
    termin: str,
):
    #обращаемся к 1 лабе
    return JSONResponse(
        "1", status_code=status.HTTP_200_OK
    )


@router.get("/second")
def lab2(
    smth
):
    #обращаемся к 2 лабе
    return JSONResponse(
        "1", status_code=status.HTTP_200_OK
    )


@router.get("/third")
def lab3(
    smth
):
    #обращаемся к 3 лабе
    return JSONResponse(
        "1", status_code=status.HTTP_200_OK
    )