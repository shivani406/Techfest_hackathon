import asyncio
import json
import websockets
from datetime import datetime

class BinanceCollector:
    def __init__(self, symbols=None):
        if symbols is None:
            symbols = ['btcusdt', 'ethusdt']
        self.symbols = symbols
        self.ws_url = "wss://stream.binance.com:9443/ws"
        self.streams = [f"{s}@trade" for s in symbols]
        self.subscription = {"method": "SUBSCRIBE", "params": self.streams, "id": 1}

    async def connect(self, buffer):
        async with websockets.connect(self.ws_url) as ws:
            await ws.send(json.dumps(self.subscription))
            async for message in ws:
                data = json.loads(message)
                if 'e' in data and data['e'] == 'trade':
                    trade = (
                        'binance',
                        data['s'].lower(),
                        float(data['p']),
                        float(data['q']),
                        datetime.fromtimestamp(data['T'] / 1000)
                    )
                    await buffer.put(trade)