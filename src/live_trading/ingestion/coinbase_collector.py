import asyncio
import json
import websockets
from datetime import datetime

class CoinbaseCollector:
    def __init__(self, symbols=None):
        if symbols is None:
            symbols = ['BTC-USD', 'ETH-USD']
        self.symbols = symbols
        self.ws_url = "wss://ws-feed.exchange.coinbase.com"
        self.subscription = {
            "type": "subscribe",
            "product_ids": self.symbols,
            "channels": ["matches"]
        }

    async def connect(self, buffer):
        async with websockets.connect(self.ws_url) as ws:
            await ws.send(json.dumps(self.subscription))
            async for message in ws:
                data = json.loads(message)
                if data.get('type') == 'match':
                    trade = (
                        'coinbase',
                        data['product_id'].lower(),
                        float(data['price']),
                        float(data['size']),
                        datetime.fromisoformat(data['time'].replace('Z', '+00:00'))
                    )
                    await buffer.put(trade)