from redis import Redis


class RedisRepo:
    def __init__(self, conn: Redis):
        self.conn = conn

    def get_student_by_id(self, id, percent=None, attendance=None):
        res = self.conn.hgetall(f"student:{id}")
        if percent is not None:
            res['percent'.encode()] = str(percent).encode()
        if attendance is not None:
            res['attended_hours'.encode()] = str(attendance*2).encode()
        return res