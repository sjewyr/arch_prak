from contextlib import asynccontextmanager
import logging
from dynaconf import Dynaconf
from fastapi import FastAPI
from psycopg.rows import dict_row

from neo4j import GraphDatabase
import psycopg
from pymongo import MongoClient
from redis import Redis
from elasticsearch import Elasticsearch
import uvicorn
from api.pres.rest.login import login_router
from api.pres.rest.lab1 import first_router


@asynccontextmanager
def finalizer(app: FastAPI):
    yield

    try:
        app.state.pg_conn.close()
    except Exception as e:
        logging.error(f"Failed to close postgres connection: {str(e)}")

    try:
        app.state.neo_conn.close()
    except Exception as e:
        logging.error(f"Failed to close neo4j connection: {str(e)}")

    try:
        app.state.mongo_client.close()
    except Exception as e:
        logging.error(f"Failed to close mongodebil connection: {str(e)}")

    try:
        app.state.redis_conn.close()
    except Exception as e:
        logging.error(f"Failed to close postgres connection: {str(e)}")

    try:
        app.state.elastic_conn.close()
    except Exception as e:
        logging.error(f"Failed to close elasticsearch connection: {str(e)}")


class Config:
    def __init__(self, valid):
        self.valid = valid


if __name__ == "__main__":
    conf = Dynaconf(
        settings_files=[
            "config.toml",
        ]
    )
    app = FastAPI(lifespan=finalizer)
    app.state.config = Config(valid=conf.api.token_minutes)

    neo4j_conf = conf.neo4j

    postgres_conn = psycopg.connect(
        "postgresql://{conf.postgres.user}:{conf.postgres.password}@{conf.postgres.host}:{conf.postgres.port}/{conf.postgres.database}",
        row_factory=dict_row,
    )
    neo4j_conn = GraphDatabase.driver(
        f"neo4j://{neo4j_conf.host}:{neo4j_conf.port}",
        auth=(neo4j_conf.user, neo4j_conf.password),
    )
    mongo_conn = MongoClient(conf.mongo["host"], conf.mongo["port"])
    redis_conf = {"host": conf.redis.host, "port": conf.redis.port, "db": conf.redis.db}
    redis_conn = Redis(**redis_conf)
    elastic_conn = Elasticsearch(f"http://{conf.elasticsearch.host}:{conf.elasticsearch.port}")

    app.state.pg_conn = postgres_conn
    app.state.neo_conn = neo4j_conn
    app.state.mongo_client = mongo_conn
    app.state.redis_conn = redis_conn
    app.state.elastic_conn = elastic_conn

    app.include_router(login_router, prefix="/login")
    app.include_router(first_router, prefix="/first")
    uvicorn.run(app, host=conf.api.host, port=conf.api.port)
