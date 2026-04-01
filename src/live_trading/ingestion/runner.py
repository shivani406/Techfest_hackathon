import asyncio
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database.db_manager import LiveTradingDB
from binance_collector import BinanceCollector
from coinbase_collector import CoinbaseCollector

class LiveFeedRunner:
    def __init__(self, flush_interval=5, batch_size=1000):
        self.db = LiveTradingDB()
        self.buffer = asyncio.Queue()
        self.flush_interval = flush_interval
        self.batch_size = batch_size

    async def flush_buffer(self):
        while True:
            await asyncio.sleep(self.flush_interval)
            trades = []
            while not self.buffer.empty() and len(trades) < self.batch_size:
                try:
                    trades.append(self.buffer.get_nowait())
                except asyncio.QueueEmpty:
                    break
            if trades:
                self.db.insert_trades_bulk(trades)
                print(f"Flushed {len(trades)} trades")

    async def run(self):
        binance = BinanceCollector()
        coinbase = CoinbaseCollector()
        tasks = [
            asyncio.create_task(binance.connect(self.buffer)),
            asyncio.create_task(coinbase.connect(self.buffer)),
            asyncio.create_task(self.flush_buffer())
        ]
        try:
            await asyncio.gather(*tasks)
        except KeyboardInterrupt:
            print("Shutting down...")
        finally:
            for task in tasks:
                task.cancel()
            await asyncio.gather(*tasks, return_exceptions=True)
            self.db.close()

if __name__ == "__main__":
    runner = LiveFeedRunner()
    asyncio.run(runner.run())