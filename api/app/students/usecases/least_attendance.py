from datetime import date
from typing import Any, List

from api.infra.elastic.elastic_repo import ElasticRepo
from api.infra.neo4j.neo_repo import NeoRepo
from api.infra.postgres.postgres_repo import PostgresRepo
from api.infra.redis.redis_repo import RedisRepo


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
    elastic_rep = ElasticRepo(elastic)
    lectures_ids = elastic_rep.get_lectures_ids_by_termin(termin)
    neo_rep = NeoRepo(neo4j_conn)
    pairs = neo_rep.get_students_by_lectures_ids(lectures_ids, date_start, date_end)
    students = set()
    students_max = {}
    scheds = set()
    for dicts in pairs:
        students.add(dicts['s.id_stud'])
        scheds.add(dicts['ha.id_sched'])
        if not students_max.get(dicts['s.id_stud']):
            students_max[dicts['s.id_stud']] = 0 
        students_max[dicts['s.id_stud']] += 1
    
    postgres_rep = PostgresRepo(postgres_conn)
    res = postgres_rep.get_presence(list(students), list(scheds))
    result = []
    for stud_id, students_m in students_max.items():
        students_actual = res.get(stud_id, 0)
        percent = students_actual/students_m * 100
        result.append([stud_id, percent])
    
    result.sort(key=lambda x: x[1])
    least_attendance = result[:10]
    ids = [l[0] for l in least_attendance]
    redis_rep = RedisRepo(redis_conn)

    infos = [redis_rep.get_student_by_id(id_) for id_ in ids]
    result = []
    for d in infos:
        temp = {}
        for k,v in d.items():
            temp[k.decode()] = v.decode()
        result.append(temp)
            
    return result


