from api.infra.neo4j.neo_repo import NeoRepo
from api.infra.postgres.postgres_repo import PostgresRepo


def listeners_count_usecase(
    name: str,
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
    keys = ["name", "description"]
    lect = [{key: d[key] for key in keys} for d in lectures]
    result['lectures'] = lect
    neo_rep = NeoRepo(neo4j_conn)
    result['listeners_count'] = neo_rep.get_listeners_count_by_list_of_lectures([l['id_lect'] for l in lectures])
    return result
