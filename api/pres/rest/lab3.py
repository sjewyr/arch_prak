from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from api.app.dependencies import get_elastic_conn, get_mongo_client, get_neo_conn, get_pg_conn, get_redis_conn
from api.app.login_middleware import login_middleware
from api.app.students.usecases.group_details import group_details_usecase
from starlette import status


third_router = APIRouter(dependencies=[Depends(login_middleware)])

@third_router.get("/group_details")
def group_details(name: str,
    postgres_conn=Depends(get_pg_conn),
    redis_conn=Depends(get_redis_conn),
    neo4j_conn=Depends(get_neo_conn),
    mongo_conn=Depends(get_mongo_client),
    elastic_conn=Depends(get_elastic_conn)):
    res = group_details_usecase(name, postgres_conn, redis_conn, neo4j_conn, mongo_conn, elastic_conn )
    return JSONResponse(res, status_code=status.HTTP_200_OK)
