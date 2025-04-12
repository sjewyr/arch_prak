from contextlib import asynccontextmanager
import logging
from dynaconf import Dynaconf
from fastapi import FastAPI
from routers import router





class Config:
    def __init__(self, valid):
        self.valid = valid


conf = Dynaconf(settings_files=["config.toml"])
app = FastAPI()
app.state.config = Config(valid=conf.api.token_minutes)

app.include_router(router)



if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host=conf.api.host, port=conf.api.port, reload=True)
