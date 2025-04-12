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
        
    def get_listeners_count_by_list_of_lectures(self, list_ids: list[int]):
        with self.conn.session() as sess:
            res = sess.run("""
UNWIND $list_ids as x MATCH (l:Lecture {id_lect: x})--(g:Group)--(s:Student) return COUNT (DISTINCT s) AS cnt

  """, ({"list_ids": list_ids}))
            return res.data()[0].get('cnt', 0)
        
    def get_schedule_by_group(self, lectures, id_group: int):
        with self.conn.session() as sess:
            query = """
UNWIND $list_ids as x MATCH (l:Lecture {id_lect: x})-[ha:HAS_ATTENDANCE]-(g:Group {id_group: $id_group})--(s:Student) return ha.id_sched, s.id_stud
"""
            res = sess.run(query, {"list_ids": lectures, "id_group": id_group})
            return res.data()