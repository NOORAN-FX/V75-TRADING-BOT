import websockets
import asyncio
import json
import pandas as pd
from datetime import datetime
import pytz

class DerivAPI:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({'Cache-Control': 'no-cache'})
        self.connected = False
        
        # Retry connection up to 3 times
        for _ in range(3):
            try:
                response = self.session.get(API_ENDPOINT, timeout=5)
                response.raise_for_status()
                self.connected = True
                break
            except Exception:
                continue
        self.websocket = None
        self.candles = pd.DataFrame(columns=['timestamp', 'open', 'high', 'low', 'close'])
        self.active_symbol = 'R_100'  # Volatility 75 index

    async def connect(self):
        self.websocket = await websockets.connect('wss://ws.binaryws.com/websockets/v3?app_id=1089')
        await self._subscribe_ticks()

    async def _subscribe_ticks(self):
        subscribe_msg = {
            "ticks": self.active_symbol,
            "subscribe": 1,
            "style": "ticks"
        }
        await self.websocket.send(json.dumps(subscribe_msg))

    async def listen(self):
        async for message in self.websocket:
            data = json.loads(message)
            if 'tick' in data:
                await self._process_tick(data['tick'])

    async def _process_tick(self, tick):
        eat_time = datetime.fromtimestamp(tick['epoch'], tz=pytz.utc).astimezone(pytz.timezone('Africa/Nairobi'))
        
        # Check if we're in analysis window (10AM-12PM EAT)
        if 10 <= eat_time.hour < 12:
            self._update_candles(eat_time, tick['quote'])

    def _update_candles(self, timestamp, price):
        minute_str = timestamp.strftime('%Y-%m-%d %H:%M')
        
        if not self.candles.empty:
            last_candle = self.candles.iloc[-1]
            if pd.Timestamp(last_candle['timestamp']).floor('T') == pd.Timestamp(minute_str):
                # Update current candle
                self.candles.at[self.candles.index[-1], 'high'] = max(last_candle['high'], price)
                self.candles.at[self.candles.index[-1], 'low'] = min(last_candle['low'], price)
                self.candles.at[self.candles.index[-1], 'close'] = price
                return

        # Add new candle
        new_candle = {
            'timestamp': minute_str,
            'open': price,
            'high': price,
            'low': price,
            'close': price
        }
        self.candles = self.candles.append(new_candle, ignore_index=True)
        
        # Keep only last 120 candles
        if len(self.candles) > 120:
            self.candles = self.candles.iloc[-120:]

    def get_price_data(self):
        try:
            response = requests.get(API_ENDPOINT, timeout=10)
            response.raise_for_status()
            return self._parse_data(response.json())
        except Exception as e:
            raise Exception(f"API Error: {str(e)}")