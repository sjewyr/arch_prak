import logging
import neo4j
import psycopg
from psycopg.rows import dict_row
import dynaconf
import pymongo
import pymongo.collation
import pymongo.collection
import pymongo.synchronous
import pymongo.synchronous.database

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

class Neo4jConnInfo:
    def __init__(self, uri: str, user: str, password: str):
        self.uri = uri
        self.user = user
        self.password = password

class ConnInfos:
    def __init__(self, psql_str: str, neo4j: Neo4jConnInfo):
        self.psql = psql_str
        self.neo4j = neo4j





def generate_conf() -> ConnInfos:
    try:
        conf = dynaconf.Dynaconf(settings_files=['conf.toml',])
        conn_str = f"postgresql://{conf.postgres.user}:{conf.postgres.password}@{conf.postgres.host}:{conf.postgres.port}/{conf.postgres.database}"
        neo4j_conf = conf.neo4j
        neo4j_info = Neo4jConnInfo(uri = f"neo4j://{neo4j_conf.host}:{neo4j_conf.port}", user = neo4j_conf.user, password=neo4j_conf.password) 

        conn_info = ConnInfos(conn_str, neo4j_info)

        return conn_info
    except Exception as e:
        raise ConfException(str(e))



def get_connection(conn_str: str) -> psycopg.Connection:
    try:
        return psycopg.connect(conn_str, row_factory=dict_row)
    except Exception as e:
        raise PostgreSQLException(str(e))

    

def get_neo4j_conn(info: Neo4jConnInfo) -> neo4j.Neo4jDriver:
    try:
        return neo4j.GraphDatabase.driver(uri=info.uri, auth=(info.user,info.password))
    except Exception as e:
        raise Neo4jException(str(e))


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
                    s.run("CREATE (n1:Lecture {id_lect: $id_lect})", id_lect=lecture["id_lect"])
                
                for group in groups:
                    s.run("CREATE (n1:Group {id_group: $id_group})", id_group=group["id_group"])
                    cur.execute("SELECT id_lect, date FROM schedule_partitioned WHERE id_group=%s AND id_lect IS NOT NULL", (group["id_group"],))
                    res = cur.fetchall()
                    query = """
                        MERGE (g:Group {id_group: $id_group})
                        WITH g
                        UNWIND $lectures AS lect
                        MERGE (l:Lecture {id_lect: lect.id_lect})
                        CREATE (g)-[:HAS_ATTENDANCE {date: lect.date}]->(l)
                    """
                    s.run(query, lectures=res, id_group=group["id_group"])
                for stud in students:
                    s_id = stud["id_stud"]
                    g_id = stud["id_group"]

                    s.run("CREATE (n:Student {id_stud: $id})", id=s_id)
                    s.run("MATCH (n:Student {id_stud: $id_stud}) MATCH (n1:Group {id_group: $id_group}) CREATE (n)-[r:InGroup]->(n1)", id_stud=s_id, id_group=g_id)

        return True
    except Exception as e:
        raise Neo4jException(str(e))
    
def load_data_mongo_db(conn: psycopg.Connection, mdb: pymongo.synchronous.database.Database):
    try:
        m_uni: pymongo.collection.Collection = mdb.universities
        m_uni.drop()
        with conn.cursor() as cur:
            cur.execute("SELECT id_univ, name FROM universities")
            unis = cur.fetchall()
            for uni in unis:
                cur.execute("SELECT id_inst, name FROM institutes WHERE id_univ = %s", (uni['id_univ'],))
                insts = cur.fetchall()
                for inst in insts:
                    cur.execute("SELECT id_depart, name FROM departments WHERE id_inst = %s", (inst["id_inst"],))
                    deps = cur.fetchall()
                    for dep in deps:
                        cur.execute("SELECT id_group, name FROM groups WHERE id_depart = %s", (dep["id_depart"], ))
                        groups = cur.fetchall()
                        dep["groups"] = groups
                    inst["departments"] = deps
                uni["institutes"] = insts

        m_uni.insert_many(unis)
    except Exception as e:
        raise MongoDebilException(str(e))
    return True
    
def main():
    conn = None
    neo_conn = None
    try:
        conf = generate_conf()
        conn = get_connection(conf.psql)
        neo_conn = get_neo4j_conn(conf.neo4j)
        client = pymongo.MongoClient("127.0.0.1", 27017)
        db = client.test
        print(load_data_mongo_db(conn, db))
        print(load_data_neo4j(conn, neo_conn))


    except GeneratingException as e:
        logging.error(e.message())
        if conn:
            conn.close()    
        if neo_conn:
            neo_conn.close()




if __name__ == "__main__":
    main()