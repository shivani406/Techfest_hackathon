"""
Handles a single WebSocket connection, receives messages,
and forwards them to Kafka using a shared producer.
"""

import websockets
import logging
import asyncio
import json
import time
from websockets.exceptions import ConnectionClosed, WebSocketException

logger = logging.getLogger(__name__)

async def setup_websocket_connection(source_websocket_url , source_name, producer):

    #=== add reconnection / fallback logic if connection to websocket fails

    logger.info(f"Starting websocket connection for {source_name}.")

    while True:
        try:
            async with websockets.connect(
                source_websocket_url,
                user_agent_header="crypto_pipeline_data_request"
            ) as websocket:
                logger.info(f"Websocket connected to {source_name}")

                async for raw_message in websocket:

                    # for now only check for - null messages (if yes then ignore it )
                    if not raw_message or not raw_message.strip():
                        logger.warning(f"Empty message from {source_name}")
                        continue
                    
                    # add metadata to the raw message
                    data = {
                            "source_exchange" : source_name,
                            "timestamp" : time.time(),
                            "message" : raw_message
                        }
                    await producer.send(
                        f"{source_name}" , 
                        value = json.dumps(data).encode("utf-8")
                    )
        
        except ConnectionClosed as e:
            logger.error(f"WebSocket connection to {source_name} closed: {e}")
        except WebSocketException as e:
            logger.error(f"WebSocket error for {source_name}: {e}")
        except asyncio.CancelledError:  # when the connection is closed using keyboard interrupt
            logger.info(f"WebSocket task for {source_name} cancelled")
            break
        except Exception as e:
            logger.exception(f"Unexpected error in {source_name} connection: {e}")


    