from redis import Redis


class RedisRepo:
    def __init__(self, conn: Redis):
        self.conn = conn

    def get_student_by_id(self, id, percent):
        res = self.conn.hgetall(f"student:{id}")
        res['percent'.encode()] = str(percent).encode()
        return res