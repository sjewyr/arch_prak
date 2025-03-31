
from fastapi import APIRouter, Depends
from api.app.login_middleware import login_middleware


first_router = APIRouter(dependencies=[Depends(login_middleware)])

@first_router.get("/echo")
def echo(sex):
    return sex