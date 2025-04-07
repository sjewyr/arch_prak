from redis import Redis


class RedisRepo:
    def __init__(self, conn: Redis):
        self.conn = conn
