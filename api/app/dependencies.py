from fastapi import Request
from neo4j import Neo4jDriver
from psycopg import Cursor
from pymongo import MongoClient
from redis import Redis


def get_pg_conn(request: Request) -> Cursor:  # type: ignore
    with request.app.state.pg_conn.cursor() as cur:
        yield cur


def get_redis_conn(request: Request) -> Redis:
    return request.app.state.redis_conn


def get_mongo_client(request: Request) -> MongoClient:
    return request.app.state.mongo_client


def get_neo_conn(request: Request) -> Neo4jDriver:
    return request.app.state.neo_conn
