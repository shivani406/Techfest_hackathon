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

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("ingestion_manager")

EXCHANGES = {
    "binance": "wss://stream.binance.com:9443/ws/btcusdt@ticker",
    "kraken": "wss://ws.kraken.com",
    "coinbase": "wss://ws-feed.exchange.coinbase.com",
}


def db_writer_worker(queue):
    try:
        conn = psycopg2.connect(
            dbname=getenv("db_name"),
            user=getenv("db_user"),
            password=getenv("db_pass"),
            host=getenv("db_host"),
            port=getenv("db_port", "5432"),
        )
        cursor = conn.cursor()
        logger.info("db writer process started successfully")
    except Exception as e:
        logger.error(f"failed to connect to db in worker: {e}")
        return

    batch = []
    last_flush = time.time()
    # threshold lowered to $1000 for demo visibility
    whale_threshold = 5000.0

    while True:
        try:
            item = queue.get(timeout=0.5)
            exchange = item["exchange"]
            data = item["data"]

            # --- AGGRESSIVE PARSING LOGIC ---
            price, qty = 0.0, 0.0

            try:
                if exchange == "binance":
                    # binance uses 'p' (price) and 'q' (quantity)
                    price = float(data.get("p", 0))
                    qty = float(data.get("q", 0))
                elif exchange == "coinbase":
                    # coinbase uses 'price' and 'last_size'
                    price = float(data.get("price", 0))
                    qty = float(data.get("last_size", 0))
                elif exchange == "kraken":
                    # kraken ticker is a list: [id, {'c': [price, vol]}, 'ticker', 'pair']
                    if isinstance(data, list) and len(data) > 1:
                        ticker_info = data[1]
                        if isinstance(ticker_info, dict) and "c" in ticker_info:
                            price = float(ticker_info["c"][0])
                            qty = float(ticker_info["c"][1])
            except (ValueError, TypeError, IndexError):
                pass

            usd_value = price * qty
            is_whale = usd_value >= whale_threshold

            if usd_value > 0:
                batch.append((exchange, json.dumps(data), is_whale, usd_value))

            # flush if batch size hit or 2 seconds passed
            if len(batch) >= 100 or (time.time() - last_flush > 2 and batch):
                query = """
                insert into live_trades (exchange, raw_payload, is_whale, usd_value) 
                values %s
                """
                extras.execute_values(cursor, query, batch)
                conn.commit()
                logger.info(f"bulk inserted {len(batch)} rows")
                batch = []
                last_flush = time.time()

        except multiprocessing.queues.Empty:
            if batch and (time.time() - last_flush > 2):
                query = "insert into live_trades (exchange, raw_payload, is_whale, usd_value) values %s"
                extras.execute_values(cursor, query, batch)
                conn.commit()
                logger.info(f"flushed partial batch of {len(batch)} rows")
                batch = []
                last_flush = time.time()
            continue
        except Exception as e:
            logger.error(f"db worker loop error: {e}")
            conn.rollback()


async def socket_producer(name, url, queue):
    logger.info(f"starting {name} websocket...")
    while True:
        try:
            async with connect(url) as ws:
                if name == "coinbase":
                    await ws.send(
                        json.dumps(
                            {
                                "type": "subscribe",
                                "product_ids": ["BTC-USD"],
                                "channels": ["ticker"],
                            }
                        )
                    )
                elif name == "kraken":
                    await ws.send(
                        json.dumps(
                            {
                                "event": "subscribe",
                                "pair": ["BTC/USD"],
                                "subscription": {"name": "ticker"},
                            }
                        )
                    )

                async for msg in ws:
                    queue.put({"exchange": name, "data": json.loads(msg)})
        except Exception as e:
            logger.warning(f"{name} socket disconnected: {e}. reconnecting in 5s...")
            await asyncio.sleep(5)


async def main():
    queue = multiprocessing.Queue()
    db_proc = multiprocessing.Process(target=db_writer_worker, args=(queue,))
    db_proc.daemon = True
    db_proc.start()

    tasks = [socket_producer(name, url, queue) for name, url in EXCHANGES.items()]

    try:
        await asyncio.gather(*tasks)
    except KeyboardInterrupt:
        logger.info("shutdown requested...")
    finally:
        db_proc.terminate()


if __name__ == "__main__":
    asyncio.run(main())
