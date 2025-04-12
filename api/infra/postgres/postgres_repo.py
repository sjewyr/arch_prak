from psycopg import Connection, Cursor


class PostgresRepo:
    def __init__(self, conn: Cursor):
        self.conn = conn

    def get_presence(self, id_students: list[int], id_scheds: list[int]):
        query = """
        SELECT id_stud, COUNT(*) 
        FROM presence_partitioned 
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
    
    def get_discipline_by_name(self, name:str):
        res = self.conn.execute("SELECT * FROM disciplines WHERE name = %s", (name,))
        return res.fetchone()
    
    def get_lectures_by_discipline_id(self, d_id: int):
        res = self.conn.execute("SELECT * FROM lectures WHERE id_disc = %s", (d_id,))
        return res.fetchall()
    
    def get_cafedralic_lectures_by_group_name(self, name: str):
        res = self.conn.execute("SELECT * FROM lectures WHERE id_disc IN (SELECT id_disc FROM disciplines WHERE id_depart = (SELECT id_depart FROM groups WHERE name = %s))", (name,))
        return res.fetchall()
    
    def get_group_id_by_name(self, name: str):
        res = self.conn.execute("SELECT id_group FROM groups WHERE name = %s", (name,))
        return res.fetchone()['id_group']
    
    def get_cafedralic_disciplines(self, name:str):
        res = self.conn.execute("(SELECT name FROM disciplines WHERE id_depart = (SELECT id_depart FROM groups WHERE name = %s))", (name,))
        return res.fetchall()