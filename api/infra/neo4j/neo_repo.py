from neo4j import Neo4jDriver


class NeoRepo:
    def __init__(self, conn: Neo4jDriver):
        self.conn = conn

    def get_students_by_lectures_ids(self, l_ids: list[int], start_date, end_date):
        with self.conn.session() as sess:
            res = sess.run("""UNWIND $l_ids AS x MATCH (l:Lecture {id_lect: x})-[ha:HAS_ATTENDANCE]-(g:Group)-[:InGroup]-(s:Student)
WHERE DATE(ha.date) > DATE($startDate) AND DATE(ha.date) < DATE($endDate) 
RETURN DISTINCT s.id_stud, ha.id_sched""", {"l_ids": l_ids, "startDate":start_date, "endDate": end_date})
            return res.data()