from infra.neo4j.neo_repo import NeoRepo
from infra.postgres.postgres_repo import PostgresRepo
from infra.redis.redis_repo import RedisRepo


def group_details_usecase(
    name: str,
    postgres_conn,
    redis_conn,
    neo4j_conn,
    mongo_conn,
    elastic,
):
    postgres_rep = PostgresRepo(postgres_conn)
    lectures = postgres_rep.get_cafedralic_lectures_by_group_name(name)
    group_id = postgres_rep.get_group_id_by_name(name)
    disciplines = postgres_rep.get_cafedralic_disciplines(name)
    disciplines = [d['name'] for d in disciplines]
    lect_ids = [l['id_lect'] for l in lectures]
    neo_rep = NeoRepo(neo4j_conn)
    schedules = neo_rep.get_schedule_by_group(lect_ids, group_id)
    students = set()
    scheds = set()
    for dicts in schedules:
        students.add(dicts['s.id_stud'])
        scheds.add(dicts['ha.id_sched'])
    res = postgres_rep.get_presence(list(students), list(scheds))
    redis_rep = RedisRepo(redis_conn)

    infos = [redis_rep.get_student_by_id(id_, attendance=percent) for id_, percent in res.items()]
    result = {"name": name, "planned_hours": len(scheds)*2, "course": disciplines, "students": []}
    for d in infos:
        temp = {}
        for k,v in d.items():
            temp[k.decode()] = v.decode()
        result['students'].append(temp)
    return result
