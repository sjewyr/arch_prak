from neo4j import Neo4jDriver


class NeoRepo:
    def __init__(self, conn: Neo4jDriver):
        self.conn = conn
