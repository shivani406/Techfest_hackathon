import asyncio
import json
import time
import multiprocessing
import logging
import psycopg2
from psycopg2 import extras
from websockets import connect
from os import getenv
from dotenv import load_dotenv

load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("ingestion_manager")

EXCHANGES = {
    "binance": "wss://stream.binance.com:9443/ws/btcusdt@ticker",
    "kraken": "wss://ws.kraken.com",
    "coinbase": "wss://ws-feed.exchange.coinbase.com"
}

# --- DB WORKER (The "Consumer" Process) ---
def db_writer_worker(queue):
    """dedicated process to pull from queue and write to postgres in batches"""
    try:
        conn = psycopg2.connect(
            dbname=getenv("db_name"), 
            user=getenv("db_user"),
            password=getenv("db_pass"), 
            host=getenv("db_host"),
            port=getenv("db_port", "5432")
        )
        cursor = conn.cursor()
        logger.info("db writer process started successfully")
    except Exception as e:
        logger.error(f"failed to connect to db in worker: {e}")
        return

    batch = []
    last_flush = time.time()
    
    while True:
        try:
            # wait for data (timeout allows loop to check for flush timing)
            item = queue.get(timeout=0.5)
            batch.append((item['exchange'], json.dumps(item['data'])))
            
            # flush if batch size hit (100) or time limit hit (2 seconds)
            if len(batch) >= 100 or (time.time() - last_flush > 2 and batch):
                query = "insert into live_trades (exchange, raw_payload) values %s"
                extras.execute_values(cursor, query, batch)
                conn.commit()
                logger.info(f"bulk inserted {len(batch)} rows")
                batch = []
                last_flush = time.time()
                
        except multiprocessing.queues.Empty:
            # if queue is empty, check if we have a partial batch to flush
            if batch and (time.time() - last_flush > 2):
                query = "insert into live_trades (exchange, raw_payload) values %s"
                extras.execute_values(cursor, query, batch)
                conn.commit()
                logger.info(f"flushed partial batch of {len(batch)} rows")
                batch = []
                last_flush = time.time()
            continue
        except Exception as e:
            logger.error(f"db worker loop error: {e}")
            conn.rollback()

# --- WEBSOCKET PRODUCER (Async Tasks) ---
async def socket_producer(name, url, queue):
    """async task to stream from exchange and put into the shared queue"""
    logger.info(f"starting {name} websocket...")
    while True:
        try:
            async with connect(url) as ws:
                if name == "coinbase":
                    await ws.send(json.dumps({"type": "subscribe", "product_ids": ["BTC-USD"], "channels": ["ticker"]}))
                elif name == "kraken":
                    await ws.send(json.dumps({"event": "subscribe", "pair": ["BTC/USD"], "subscription": {"name": "ticker"}}))
                
                async for msg in ws:
                    queue.put({"exchange": name, "data": json.loads(msg)})
        except Exception as e:
            logger.warning(f"{name} socket disconnected: {e}. reconnecting in 5s...")
            await asyncio.sleep(5)

# --- MAIN RUNNER ---
async def main():
    # shared pipe between producers and the db process
    queue = multiprocessing.Queue()

    # start the consumer process
    db_proc = multiprocessing.Process(target=db_writer_worker, args=(queue,))
    db_proc.daemon = True # ensures it dies when main process stops
    db_proc.start()

    # start all exchange producers as async tasks
    tasks = [socket_producer(name, url, queue) for name, url in EXCHANGES.items()]
    
    try:
        await asyncio.gather(*tasks)
    except KeyboardInterrupt:
        logger.info("shutdown requested...")
    finally:
        db_proc.terminate()
        logger.info("ingestion stopped")

if __name__ == "__main__":
    asyncio.run(main())