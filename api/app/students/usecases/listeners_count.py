from infra.neo4j.neo_repo import NeoRepo
from infra.postgres.postgres_repo import PostgresRepo


def listeners_count_usecase(
    name: str,
    year: int,
    postgres_conn,
    redis_conn,
    neo4j_conn,
    mongo_conn,
    elastic,
):
    postgres_rep = PostgresRepo(postgres_conn)
    discipline = postgres_rep.get_discipline_by_name(name)
    result = {"name": discipline["name"], "description": discipline["description"]}
    lectures = postgres_rep.get_lectures_by_discipline_id(discipline["id_disc"])
    
    lecture_ids = [l['id_lect'] for l in lectures]
    
    neo_rep = NeoRepo(neo4j_conn)

    listeners_per_lecture = neo_rep.get_listeners_count_per_lecture(lecture_ids, year)
    listeners_dict = {item['id_lect']: item['count'] for item in listeners_per_lecture}
    
    keys = ["name", "description", "is_pracise"]
    lect = []
    for lecture in lectures:
        lecture_data = {key: lecture[key] for key in keys}
        lecture_data['listeners_count'] = listeners_dict.get(lecture['id_lect'], 0)
        if lecture_data['listeners_count'] != 0:
            lect.append(lecture_data)
    
    result['lectures'] = lect
    result['year'] = f'{year} - {year + 1}'
    return result