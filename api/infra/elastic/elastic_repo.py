from elasticsearch import Elasticsearch

class ElasticRepo:
    def __init__(self, conn: Elasticsearch):
        self.conn = conn

    def get_lectures_ids_by_termin(self, termin) -> list[int]:
        res = self.conn.search(index="lectures_text", query={"match": {"description": {"query": termin}}})
        if res['hits']:
            print([result["_source"]["id_lect"] for result in res['hits']['hits']])
            return [result["_source"]["id_lect"] for result in res['hits']['hits']]
        return []