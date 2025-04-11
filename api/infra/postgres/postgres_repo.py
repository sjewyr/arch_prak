from psycopg import Connection, Cursor


class PostgresRepo:
    def __init__(self, conn: Cursor):
        self.conn = conn

    def get_presence(self, id_students: list[int], id_scheds: list[int]):
        query = """
        SELECT id_stud, COUNT(*) 
        FROM presence 
        WHERE id_stud = ANY(%(id_students)s) 
          AND id_sched = ANY(%(id_scheds)s)
        GROUP BY id_stud

    """
        self.conn.execute(query, {"id_students": id_students, "id_scheds": id_scheds})
        res = self.conn.fetchall()
        res_ = {}
        for d in res:
            res_[d["id_stud"]] = d["count"]
        return res_