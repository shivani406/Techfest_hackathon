"""
Main entry point for the crypto data pipeline.
Creates a shared Kafka producer and starts WebSocket connections for all exchanges.
"""

import asyncio
import signal
import logging
import aiokafka
import json
from logging_setup import init_logging
from setup_connection.source_url_connections import setup_websocket_connection


init_logging()
logger = logging.getLogger(__name__)
    # Websocket Exchanges

exchanges = {
        "binance": "wss://ws-api.binance.com:443/ws-api/v3"
                    # "coinbase": "wss://ws-feed.exchange.coinbase.com"
        }
        # === Add more exchanges and their websocket URLs here

# Create a single kafka producer to be shared by all the exchanges
async def create_kafka_producer():

    producer = aiokafka.AIOKafkaProducer(
        bootstrap_servers='localhost:9092',
        client_id="crypto-pipeline-shared-producer",
        value_serializer=lambda v: json.dumps(v).encode("utf-8"),
        linger_ms=10

        #=== add more data compression techniques here
    )
    await producer.start()
    logger.info("Kafka Producer started")
    return producer

# function to handle all the keyboard interrupt
async def shutdown(signal , loop, producer , tasks):
    # to stop the producer when keyboard interrupt happens

    logger.info("Recieved Stop signal (Keyboard Interrupt)")
    # first cancel each task
    for task in tasks:
        task.cancel()
    await asyncio.gather(*tasks, return_exceptions=True)
    await producer.stop()
    loop.stop()


async def main():
    producer = await create_kafka_producer()

    # create one websocket task per exchange
    tasks = []
    for source_name, source_url in exchanges.items():
        task = asyncio.create_task(setup_websocket_connection(
            source_name= source_name, 
            source_websocket_url= source_url, 
            producer= producer))
        
        tasks.append(task)
    logger.info("All tasks created for all exchange url")

    # Handle graceful shutdown on SIGINT (Keyboard interrupt)
    loop = asyncio.get_running_loop()

    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler
        (sig, lambda s=sig: asyncio.create_task(shutdown(s, loop, producer, tasks)))
    try:
        await asyncio.gather(*tasks)
    except asyncio.CancelledError:
        pass #===  in case of shutdown close the producer also
    finally:
        await producer.stop()
        logger.info("Producer Stopped.")

if __name__ == "__main__":
    asyncio.run(main())


