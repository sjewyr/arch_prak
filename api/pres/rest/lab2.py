from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from app.dependencies import get_elastic_conn, get_mongo_client, get_neo_conn, get_pg_conn, get_redis_conn
from app.students.usecases.listeners_count import listeners_count_usecase

from starlette import status


second_router = APIRouter()

@second_router.get("/listeners_count")
def listeners_count(name: str,
    postgres_conn=Depends(get_pg_conn),
    redis_conn=Depends(get_redis_conn),
    neo4j_conn=Depends(get_neo_conn),
    mongo_conn=Depends(get_mongo_client),
    elastic_conn=Depends(get_elastic_conn)):
    res = listeners_count_usecase(name, postgres_conn, redis_conn, neo4j_conn, mongo_conn, elastic_conn )
    return JSONResponse(res, status_code=status.HTTP_200_OK)
