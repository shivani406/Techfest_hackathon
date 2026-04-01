import psycopg2
from psycopg2.extras import execute_values
import os
import json # add this import

class databasemanager:
    def __init__(self):
        self.conn = psycopg2.connect(
            dbname=os.getenv("db_name", "crypto_db"),
            user=os.getenv("db_user", "postgres"),
            password=os.getenv("db_pass"),
            host=os.getenv("db_host", "localhost"),
            port=os.getenv("db_port", "5432")
        )
        self.create_tables()

    def create_tables(self):
        query = """
        create table if not exists raw_content (
            id serial primary key,
            source varchar(50),
            external_id varchar(255) unique,
            content_type varchar(50),
            raw_data jsonb,
            created_at timestamp default current_timestamp
        );
        """
        with self.conn.cursor() as cur:
            cur.execute(query)
            self.conn.commit()

    def save_batch(self, source, items):
        query = """
        insert into raw_content (source, external_id, content_type, raw_data)
        values %s on conflict (external_id) do nothing
        """
        # wrap the item['data'] dict in json.dumps()
        data = [
            (source, item['id'], item['type'], json.dumps(item['data'])) 
            for item in items
        ]
        
        with self.conn.cursor() as cur:
            execute_values(cur, query, data)
            self.conn.commit()