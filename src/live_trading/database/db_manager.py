import psycopg2
from ...shared.config import Config

class LiveTradingDB:
    def __init__(self):
        self.conn = None
        self.cursor = None
        self._connect()
        self._create_table()

    def _connect(self):
        self.conn = psycopg2.connect(
            host=Config.POSTGRES_HOST,
            port=Config.POSTGRES_PORT,
            dbname=Config.POSTGRES_DB,
            user=Config.POSTGRES_USER,
            password=Config.POSTGRES_PASSWORD
        )
        self.cursor = self.conn.cursor()

    def _create_table(self):
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS trades (
            id SERIAL PRIMARY KEY,
            exchange TEXT,
            symbol TEXT,
            price NUMERIC,
            volume NUMERIC,
            trade_time TIMESTAMP,
            received_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)
        self.conn.commit()

    def insert_trades_bulk(self, trade_list):
        if not trade_list:
            return
        self.cursor.executemany("""
        INSERT INTO trades (exchange, symbol, price, volume, trade_time)
        VALUES (%s, %s, %s, %s, %s)
        """, trade_list)
        self.conn.commit()

    def close(self):
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()