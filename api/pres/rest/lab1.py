from datetime import date
from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from api.app.dependencies import (
    get_mongo_client,
    get_neo_conn,
    get_pg_conn,
    get_redis_conn,
    get_elastic_conn
)
from api.app.login_middleware import login_middleware
from starlette import status

from api.app.students.usecases.least_attendance import least_attendance_usecase


first_router = APIRouter(dependencies=[Depends(login_middleware)])


@first_router.get("/least_attendance")
def least_attendance(
    date_start: date,
    date_end: date,
    termin: str,
    postgres_conn=Depends(get_pg_conn),
    redis_conn=Depends(get_redis_conn),
    neo4j_conn=Depends(get_neo_conn),
    mongo_conn=Depends(get_mongo_client),
    elastic_conn=Depends(get_elastic_conn)  # YA ZDELAL VRODE
):
    res = least_attendance_usecase(
        date_start,
        date_end,
        termin,
        postgres_conn,
        redis_conn,
        neo4j_conn,
        mongo_conn,
        elastic_conn
    )
    res['start_date'] = date_start.isoformat()
    res['end_date'] = date_end.isoformat()
    res['termin'] = termin
    return JSONResponse(
        res, status_code=status.HTTP_200_OK
    )
