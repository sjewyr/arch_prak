from datetime import date
from typing import Any, List


def least_attendance_usecase(
    date_start: date,
    date_end: date,
    termin: str,
    postgres_conn,
    redis_conn,
    neo4j_conn,
    mongo_conn,
    elastic,
) -> List[Any]:
    return None
