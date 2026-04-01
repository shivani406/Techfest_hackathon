import asyncio
import json
import aiokafka
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

class trades_db_manager:
    def __init__(self):
        self.conn = psycopg2.connect(
            dbname=os.getenv("db_name"),
            user=os.getenv("db_user"),
            password=os.getenv("db_pass"),
            host=os.getenv("db_host"),
            port=os.getenv("db_port", "5432")
        )
        self.init_db()

    def init_db(self):
        query = """
        create table if not exists live_trades (
            id serial primary key,
            exchange varchar(50),
            raw_payload jsonb,
            received_at timestamp default current_timestamp
        );
        """
        with self.conn.cursor() as cur:
            cur.execute(query)
            self.conn.commit()

    async def start_consuming(self):
        consumer = aiokafka.AIOKafkaConsumer(
            "binance", "kraken", "coinbase",
            bootstrap_servers="localhost:9092",
            group_id="trade_consumer_group",
            value_deserializer=lambda v: json.loads(v.decode("utf-8"))
        )
        await consumer.start()
        print("db manager started consuming from kafka...")
        try:
            async for msg in consumer:
                self.save_to_postgres(msg.value)
        finally:
            await consumer.stop()

    def save_to_postgres(self, data):
        query = "insert into live_trades (exchange, raw_payload) values (%s, %s)"
        with self.conn.cursor() as cur:
            cur.execute(query, (data['source_exchange'], json.dumps(data['message'])))
            self.conn.commit()

if __name__ == "__main__":
    db_worker = trades_db_manager()
    asyncio.run(db_worker.start_consuming())