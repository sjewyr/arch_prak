from elasticsearch import Elasticsearch

class ElasticRepo:
    def __init__(self, conn: Elasticsearch):
        self.conn = conn