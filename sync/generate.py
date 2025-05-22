import logging
import random
import time
import neo4j
import pymongo.database
import redis
import psycopg
from psycopg.rows import dict_row
import dynaconf
import pymongo
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk

logging.basicConfig(level=logging.INFO)


class GeneratingException(Exception):
    def __init__(self, text):
        self.text = text

    def message(self):
        return self.text


class ConfException(GeneratingException):
    def __init__(self, text):
        super().__init__(text)

    def message(self):
        return "Ошибка при загрузке конфига: " + super().message()


class PostgreSQLException(GeneratingException):
    def __init__(self, text):
        super().__init__(text)

    def message(self):
        return "Ошибка при подключении к PostgreSQL: " + super().message()


class Neo4jException(GeneratingException):
    def __init__(self, text):
        super().__init__(text)

    def message(self):
        return "Ошибка при загрузке в Neo4j: " + super().message()


class MongoDebilException(GeneratingException):
    def __init__(self, text):
        super().__init__(text)

    def message(self):
        return "Ошибка при загрузке в MongoDB: " + super().message()


class RediskaException(GeneratingException):
    def __init__(self, text):
        super().__init__(text)

    def message(self):
        return "Ошибка при загрузке в Redis: " + super().message()

class ElasticsearchException(GeneratingException):
    def __init__(self, text):
        super().__init__(text)

    def message(self):
        return "Ошибка при загрузке в Elasticsearch: " + super().message()

class ConnInfos:
    def __init__(
        self,
        psql_str: str,
        neo4j: dict[str, str],
        redis: dict[str, str],
        mongo: dict[str, str | int],
        elastic: dict[str, str | int]
    ):
        self.psql = psql_str
        self.neo4j = neo4j
        self.redis = redis
        self.mongo = mongo
        self.elastic = elastic


def generate_conf() -> ConnInfos:
    try:
        conf = dynaconf.Dynaconf(
            settings_files=[
                "config.toml",
            ]
        )
        conf.reload()
        conn_str = f"postgresql://{conf.postgres.user}:{conf.postgres.password}@{conf.postgres.host}:{conf.postgres.port}/{conf.postgres.database}"
        neo4j_conf = conf.neo4j
        neo4j_info = {
            "uri": f"neo4j://{neo4j_conf.host}:{neo4j_conf.port}",
            "user": neo4j_conf.user,
            "password": neo4j_conf.password,
        }
        redis = {"host": conf.redis.host, "port": conf.redis.port, "db": conf.redis.db}
        mongo_conf = conf.mongo
        mongo = {"host": mongo_conf.host, "port": mongo_conf.port, "db": mongo_conf.db}
        elastic_conf = conf.elasticsearch
        elastic = {"host": elastic_conf.host, "port": elastic_conf.port}

        conn_info = ConnInfos(conn_str, neo4j_info, redis, mongo, elastic)
        logging.info("Конфиг загружен")

        return conn_info
    except Exception as e:
        raise ConfException(str(e))


def load_data_neo4j(conn: psycopg.Connection, neo_conn: neo4j.Neo4jDriver):
    try:
        with neo_conn.session() as s:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM students")
                students = cur.fetchall()
                cur.execute("SELECT * FROM groups")
                groups = cur.fetchall()
                cur.execute("SELECT * FROM lectures")
                lectures = cur.fetchall()
                s.run("MATCH (n1:Student) DETACH DELETE n1;")
                s.run("MATCH (n1:Group) DETACH DELETE n1;")
                s.run("MATCH (n1:Lecture) DETACH DELETE n1;")
                for lecture in lectures:
                    s.run(
                        "CREATE (n1:Lecture {id_lect: $id_lect})",
                        id_lect=lecture["id_lect"],
                    )

                for group in groups:
                    s.run(
                        "CREATE (n1:Group {id_group: $id_group})",
                        id_group=group["id_group"],
                    )
                    cur.execute(
                        "SELECT id_sched, id_lect, date FROM schedule_partitioned WHERE id_group=%s AND id_lect IS NOT NULL",
                        (group["id_group"],),
                    )
                    res = cur.fetchall()
                    query = """
                        MERGE (g:Group {id_group: $id_group})
                        WITH g
                        UNWIND $lectures AS lect
                        MERGE (l:Lecture {id_lect: lect.id_lect})
                        CREATE (g)-[:HAS_ATTENDANCE {date: lect.date, id_sched:lect.id_sched}]->(l)
                    """
                    s.run(query, lectures=res, id_group=group["id_group"])
                for stud in students:
                    s_id = stud["id_stud"]
                    g_id = stud["id_group"]

                    s.run("CREATE (n:Student {id_stud: $id})", id=s_id)
                    s.run(
                        "MATCH (n:Student {id_stud: $id_stud}) MATCH (n1:Group {id_group: $id_group}) CREATE (n)-[r:InGroup]->(n1)",
                        id_stud=s_id,
                        id_group=g_id,
                    )
        logging.info("В Neo4j все записано.")
        return True
    except Exception as e:
        raise Neo4jException(str(e))


def load_data_mongo_db(
    conn: psycopg.Connection, mdb: pymongo.synchronous.database.Database
):
    try:
        m_uni: pymongo.collection.Collection = mdb.universities
        m_uni.drop()
        with conn.cursor() as cur:
            cur.execute("SELECT id_univ, name FROM universities")
            unis = cur.fetchall()
            for uni in unis:
                cur.execute(
                    "SELECT id_inst, name FROM institutes WHERE id_univ = %s",
                    (uni["id_univ"],),
                )
                insts = cur.fetchall()
                for inst in insts:
                    cur.execute(
                        "SELECT id_depart, name FROM departments WHERE id_inst = %s",
                        (inst["id_inst"],),
                    )
                    deps = cur.fetchall()
                    for dep in deps:
                        cur.execute(
                            "SELECT id_group, name FROM groups WHERE id_depart = %s",
                            (dep["id_depart"],),
                        )
                        groups = cur.fetchall()
                        dep["groups"] = groups
                    inst["departments"] = deps
                uni["institutes"] = insts

        m_uni.insert_many(unis)
        logging.info("В Монгодебила все записано.")
    except Exception as e:
        raise MongoDebilException(str(e))
    return True


def load_data_redis(conn: psycopg.Connection, redis_conn):
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT id_stud, id_group, name, studak, age FROM students")
            students = cur.fetchall()
            for student in students:
                student_id = student["id_stud"]
                student_data = {
                    "id_group": student["id_group"],
                    "name": student["name"],
                    "studak": student["studak"],
                    "age": student["age"],
                }
                redis_conn.hset(f"student:{student_id}", mapping=student_data)

        logging.info("В Редиску все записано.")
    except Exception as e:
        raise RediskaException(str(e))
    return True

academic_verbs = [
    "анализируется", "рассматривается", "исследуется", "выявляется",
    "определяется", "оценивается", "обосновывается", "моделируется",
    "структурируется", "проецируется", "интерпретируется"
]

subjects = [
    "когнитивная природа сознания", "историческая ретроспектива модерна",
    "функционирование социальных институтов", "гносеологические аспекты восприятия",
    "онтология языка", "структура математической абстракции",
    "динамика культурных трансформаций", "семантика знаковых систем",
    "сравнительный анализ методологических подходов", "эволюция научной парадигмы"
]

fancy_nouns = [
    "когнитивный дискурс", "эпистемологическая платформа", "трансцендентальная модель",
    "метаязык мышления", "парадигма постструктурализма", "онтологический модус",
    "интерсубъективная картина", "дедуктивная конструкция", "аксиоматическая система"
]

adjectives = [
    "глубокий", "детальный", "комплексный", "спорный", "многоаспектный",
    "парадоксальный", "всесторонний", "противоречивый", "инновационный"
]

def generate_random_paragraph():
    paragraph = []
    for _ in range(random.randint(4, 6)):
        subject = random.choice(subjects)
        verb = random.choice(academic_verbs)
        noun = random.choice(fancy_nouns)
        adj = random.choice(adjectives)

        #данной
        sentence = (
            f"В рамках данной части лекции {verb} {subject}, где особое внимание уделяется такому явлению, как {adj} {noun}. "
            f"Этот подход позволяет расширить представление о теме за счёт включения междисциплинарных связей и критического анализа."
        )
        paragraph.append(sentence)
    return " ".join(paragraph)

def generate_description():
    body = generate_random_paragraph()
    outro = random.choice([
        "В результате рассмотрения слушатель получает новый взгляд на предмет.",
        "Такой анализ создаёт фундамент для дальнейших размышлений.",
        "Таким образом, создаётся концептуальная база для более глубокого осмысления.",
        "Подобный подход обеспечивает целостное понимание изучаемых процессов.",
        "Итогом лекции становится расширение границ привычного восприятия темы."
    ])
    return f"{body} {outro}"

def load_data_elasticsearch(conn, elastic_conn):
    try:
        index_name = "lectures_text"
        if not elastic_conn.indices.exists(index=index_name):
            elastic_conn.indices.create(index=index_name)

        with conn.cursor() as cur:
            cur.execute("SELECT id_lect FROM lectures")
            lectures = cur.fetchall()

            actions = []
            for lecture in lectures:
                lect_id = lecture["id_lect"]
                doc = {
                    "_index": index_name,
                    "_id": lect_id,
                    "id_lect": lect_id,
                    "description": generate_description()
                }
                actions.append(doc)

            if actions:
                bulk(elastic_conn, actions)

        logging.info("В Elasticsearch все записано.")
        return True
    except Exception as e:
        raise ElasticsearchException(str(e))



def main(
    conn: psycopg.Connection,
    neo_conn: neo4j.Neo4jDriver,
    db_mongo: pymongo.database.Database,
    redis_conn: redis.Redis,
    elastic_conn: Elasticsearch
):
    try:
        load_data_mongo_db(conn, db_mongo)
        time.sleep(15)
        load_data_redis(conn, redis_conn)
        load_data_elasticsearch(conn, elastic_conn)
        load_data_neo4j(conn, neo_conn)

    except GeneratingException as e:
        logging.error(e.message())


if __name__ == "__main__":
    conf = generate_conf()
    time.sleep(10)
    with psycopg.connect(conf.psql, row_factory=dict_row) as conn:
        with pymongo.MongoClient(
            conf.mongo["host"], conf.mongo["port"]
        ) as mongo_client:
            with neo4j.GraphDatabase.driver(
                conf.neo4j.get("uri"),
                auth=(conf.neo4j.get("user"), conf.neo4j.get("password")),
            ) as neo_conn:
                with redis.Redis(**conf.redis) as redis_conn:
                    elastic_conn = Elasticsearch(f"http://{conf.elastic['host']}:{conf.elastic['port']}") 
                    db = mongo_client[conf.mongo.get("db")]
                    main(conn, neo_conn, db, redis_conn, elastic_conn)

#проверка на наличие плагинов
#  curl http://localhost:8083/connectors/elasticsearch-sink/status | jq
#  curl http://localhost:8083/connectors/debezium-postgres-connector/status | jq
#  curl http://localhost:8083/connectors/redis/status | jq


#загрузка
# curl -X POST -H "Content-Type: application/json" \
#  --data @connectors/debezium-config.json \
#  http://localhost:8083/connectors


#загрузка
# curl -X POST -H "Content-Type: application/json" \
#  --data @connectors/redis-config.json \
#  http://localhost:8083/connectors

# curl -X POST -H "Content-Type: application/json" \
#  --data @connectors/elastic-config.json \
#  http://localhost:8083/connectors

# проверка что данные появились и в elastic
# curl -X GET "http://localhost:9200/postgres-server.public.presence/_search?q=id_pres:9281251&pretty"

#      "topics": "postgres-server.public.presence",  
#надо чето думать, потому что * не работает