import websockets
import logging
import asyncio
import json
import time
from websockets.exceptions import ConnectionClosed, WebSocketException

logger = logging.getLogger(__name__)

async def setup_websocket_connection(source_websocket_url, source_name, producer):
    logger.info(f"starting websocket connection for {source_name}")
    while True:
        try:
            async with websockets.connect(source_websocket_url) as websocket:
                # coinbase requires a subscription message
                if source_name == "coinbase":
                    subscribe_msg = {
                        "type": "subscribe",
                        "product_ids": ["BTC-USD"],
                        "channels": ["ticker"]
                    }
                    await websocket.send(json.dumps(subscribe_msg))
                
                async for raw_message in websocket:
                    if not raw_message: continue
                    
                    data = {
                        "source_exchange": source_name,
                        "timestamp": time.time(),
                        "message": json.loads(raw_message)
                    }
                    await producer.send(source_name, data)
        except (ConnectionClosed, WebSocketException) as e:
            logger.error(f"websocket error for {source_name}: {e}. reconnecting in 5s...")
            await asyncio.sleep(5)
        except asyncio.CancelledError:
            break
        except Exception as e:
            logger.exception(f"unexpected error in {source_name}: {e}")
            await asyncio.sleep(5)