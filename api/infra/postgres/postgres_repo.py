from psycopg import Connection


class PostgresRepo:
    def __init__(self, conn: Connection):
        self.conn = conn
