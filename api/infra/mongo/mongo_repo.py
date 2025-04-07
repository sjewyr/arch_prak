from pymongo import MongoClient


class MongoRepo:
    def __init__(self, conn: MongoClient):
        self.conn = conn
