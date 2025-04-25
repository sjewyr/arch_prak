from neo4j import Neo4jDriver
import datetime


class NeoRepo:
    def __init__(self, conn: Neo4jDriver):
        self.conn = conn

    def get_students_by_lectures_ids(self, l_ids: list[int], start_date, end_date):
        with self.conn.session() as sess:
            res = sess.run("""UNWIND $l_ids AS x MATCH (l:Lecture {id_lect: x})-[ha:HAS_ATTENDANCE]-(g:Group)-[:InGroup]-(s:Student)
WHERE DATE(ha.date) > DATE($startDate) AND DATE(ha.date) < DATE($endDate) 
RETURN DISTINCT s.id_stud, ha.id_sched""", {"l_ids": l_ids, "startDate":start_date, "endDate": end_date})
            return res.data()
    
    def get_listeners_count_per_lecture(self, list_ids: list[int], year: int):
        year1 = datetime.date.fromisoformat(f"{year}-01-01")
        year2 = datetime.date.fromisoformat(f"{year+1}-01-01")
        with self.conn.session() as sess:
            res = sess.run("""
                UNWIND $list_ids as x 
                MATCH (l:Lecture {id_lect: x})-[ha:HAS_ATTENDANCE]-(g:Group)--(s:Student) 
                WHERE DATE(ha.date) > DATE($year1) AND DATE(ha.date) < DATE($year2) 
                RETURN l.id_lect as id_lect, COUNT(DISTINCT s) AS count
                """, list_ids=list_ids, year1 = year1, year2 = year2)
            
            records = list(res)  
            return [{"id_lect": record["id_lect"], "count": record["count"]} for record in records]
        
        
    def get_schedule_by_group(self, lectures, id_group: int):
        with self.conn.session() as sess:
            query = """
UNWIND $list_ids as x MATCH (l:Lecture {id_lect: x})-[ha:HAS_ATTENDANCE]-(g:Group {id_group: $id_group})--(s:Student) return ha.id_sched, s.id_stud
"""
            res = sess.run(query, {"list_ids": lectures, "id_group": id_group})
            return res.data()