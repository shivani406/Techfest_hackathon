import asyncio
import signal
import logging
import aiokafka
import json
from logging_setup import init_logging
from source_url_connections import setup_websocket_connection

init_logging()
logger = logging.getLogger(__name__)

exchanges = {
    "binance": "wss://stream.binance.com:9443/ws/btcusdt@ticker",
    "kraken": "wss://ws.kraken.com",
    "coinbase": "wss://ws-feed.exchange.coinbase.com"
}

async def create_kafka_producer():
    producer = aiokafka.AIOKafkaProducer(
        bootstrap_servers="localhost:9092",
        client_id="crypto-pipeline-shared-producer",
        value_serializer=lambda v: json.dumps(v).encode("utf-8"),
        linger_ms=10
    )
    await producer.start()
    logger.info("kafka producer started")
    return producer

async def shutdown(sig, loop, producer, tasks):
    logger.info(f"received stop signal: {sig.name}")
    for task in tasks:
        task.cancel()
    await asyncio.gather(*tasks, return_exceptions=True)
    await producer.stop()
    loop.stop()

async def main():
    producer = await create_kafka_producer()
    tasks = []
    for name, url in exchanges.items():
        task = asyncio.create_task(
            setup_websocket_connection(
                source_websocket_url=url,
                source_name=name,
                producer=producer
            )
        )
        tasks.append(task)
    
    logger.info("all exchange tasks initialized")
    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, lambda s=sig: asyncio.create_task(shutdown(s, loop, producer, tasks)))

    try:
        await asyncio.gather(*tasks)
    except asyncio.CancelledError:
        pass
    finally:
        await producer.stop()
        logger.info("producer stopped")

if __name__ == "__main__":
    asyncio.run(main())