from dynaconf import Dynaconf
from fastapi import FastAPI
import uvicorn
from api.pres.rest.login import login_router
from api.pres.rest.lab1 import first_router

class Config:
    def __init__(self, valid):
        self.valid = valid

if __name__ == "__main__":
    conf = Dynaconf(settings_files=['config.toml',])
    app = FastAPI()
    app.state.config = Config(valid=conf.api.token_minutes)
    app.include_router(login_router, prefix="/login")
    app.include_router(first_router, prefix='/first')
    uvicorn.run(app, host=conf.api.host, port= conf.api.port)