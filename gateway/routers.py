import datetime
import json
import requests
from fastapi import APIRouter, Form, Request, Response, Depends, HTTPException
from fastapi.responses import JSONResponse
from login_utils import encode_token
from starlette import status
from login_utils import login_middleware


router = APIRouter(dependencies=[Depends(login_middleware)])
login_router = APIRouter()


@login_router.post("/login")
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


@login_router.post("/logout")
def logout(response: Response):
    response.set_cookie("access_token", "")
    return JSONResponse(status_code=status.HTTP_204_NO_CONTENT)



@router.get("/first")
def lab1(
    date_start: datetime.date,
    date_end: datetime.date,
    termin: str,
):
    params = {
        "date_start": date_start,
        "date_end": date_end,
        "termin": termin
    }
    
    try:
        response = requests.get(f"http://api:10000/least_attendance", params=params)
        response.raise_for_status()
        return JSONResponse(response.json(), status_code=200)
    except requests.exceptions.RequestException as e:
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка при запросе к least_attendance: {str(e)}"
        )


@router.get("/second")
def lab2(
    name: str,
    year: int
):
    
    params = {
        "name": name,
        "year": year
    }

    try:
        response = requests.get(f"http://api:10000/listeners_count", params=params)
        response.raise_for_status()
        return JSONResponse(response.json(), status_code=200)
    except requests.exceptions.RequestException as e:
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка при запросе к listeners_count: {str(e)}"
        )



@router.get("/third")
def lab3(
    name: str
):
    params = {
        "name": name
    }

    try:
        response = requests.get(f"http://api:10000/group_details", params=params)
        response.raise_for_status()
        return JSONResponse(response.json(), status_code=200)
    except requests.exceptions.RequestException as e:
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка при запросе к listeners_count: {str(e)}"
        )