from contextlib import asynccontextmanager
import logging
from dynaconf import Dynaconf
from fastapi import FastAPI
from psycopg.rows import dict_row
from neo4j import GraphDatabase
import psycopg
import time
import os
from pymongo import MongoClient
from redis import Redis
from elasticsearch import Elasticsearch
from pres.rest.lab1 import first_router
from pres.rest.lab2 import second_router
from pres.rest.lab3 import third_router

@asynccontextmanager
async def finalizer(app: FastAPI):
    neo4j_conf = conf.neo4j
    time.sleep(10)
    app.state.pg_conn = psycopg.connect(
        f"postgresql://{conf.postgres.user}:{conf.postgres.password}@{conf.postgres.host}:{conf.postgres.port}/{conf.postgres.database}",
        row_factory=dict_row,
    )
    app.state.neo_conn = GraphDatabase.driver(
        f"neo4j://{neo4j_conf.host}:{neo4j_conf.port}",
        auth=(neo4j_conf.user, neo4j_conf.password),
    )
    app.state.mongo_client = MongoClient(conf.mongo["host"], conf.mongo["port"])
    redis_conf = {"host": conf.redis.host, "port": conf.redis.port, "db": conf.redis.db}
    app.state.redis_conn = Redis(**redis_conf)
    app.state.elastic_conn = Elasticsearch(f"http://{conf.elasticsearch.host}:{conf.elasticsearch.port}")


    match str(os.getenv("LAB_NUM")):
        case "1":
            app.include_router(first_router, tags=["LAB 1"])
        case "2":
            app.include_router(second_router, tags=["LAB 2"])
        case "3":
            app.include_router(third_router, tags=["LAB 3"])

    yield

    connections = [
        ('pg_conn', 'postgres'),
        ('neo_conn', 'neo4j'),
        ('mongo_client', 'mongodb'),
        ('redis_conn', 'redis'),
        ('elastic_conn', 'elasticsearch')
    ]

    for attr, name in connections:
        try:
            if hasattr(app.state, attr):
                conn = getattr(app.state, attr)
                if conn:
                    conn.close()
        except Exception as e:
            logging.error(f"Failed to close {name} connection: {str(e)}")

class Config:
    def __init__(self, valid):
        self.valid = valid


conf = Dynaconf(settings_files=["config.toml"])
app = FastAPI(lifespan=finalizer)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host=conf.api.host, port=conf.api.port, reload=True)
