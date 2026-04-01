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
            # CHANGING the group_id forces Kafka to treat this as a brand new user
            group_id="trade_consumer_new_test_1", 
            # 'earliest' tells it to go back to the very first message ever sent
            auto_offset_reset="earliest",       
            value_deserializer=lambda v: json.loads(v.decode("utf-8")),
            allow_auto_create_topics=True
        )
        await consumer.start()
        print("consumer is online and looking for old messages...")
        try:
            async for msg in consumer:
                print(f"received data from {msg.topic}") # Add this to see it live
                self.save_to_postgres(msg.value)
        finally:
            await consumer.stop()

    def save_to_postgres(self, data):
        query = "insert into live_trades (exchange, raw_payload) values (%s, %s)"
        try:
            with self.conn.cursor() as cur:
                # Ensure the dict is converted to a JSON string
                payload_json = json.dumps(data['message'])
                cur.execute(query, (data['source_exchange'], payload_json))
                self.conn.commit() # Critical: Ensure this is inside the try
                print(f"Stored message from {data['source_exchange']}") 
        except Exception as e:
            print(f"DB Error: {e}")
            self.conn.rollback() # Rollback on error to keep connection alive

if __name__ == "__main__":
    db_worker = trades_db_manager()
    asyncio.run(db_worker.start_consuming())