import pytz
from datetime import datetime, timedelta
import pandas as pd
import asyncio

class TimeUtils:
    EAT = pytz.timezone('Africa/Nairobi')

    @classmethod
    def current_eat_time(cls):
        return datetime.now(cls.EAT)

    @classmethod
    def is_analysis_window(cls):
        now = cls.current_eat_time()
        return 10 <= now.hour < 12

class CandleManager:
    def __init__(self):
        self.candles = pd.DataFrame(columns=['timestamp', 'open', 'high', 'low', 'close'])
        self.max_candles = 120

    def update_candles(self, new_candle):
        if len(self.candles) >= self.max_candles:
            self.candles = self.candles.iloc[1:]
        self.candles = self.candles.append(new_candle, ignore_index=True)

    def get_recent_candles(self, count=10):
        return self.candles.tail(count)

async def time_until_target(hour=12, minute=0):
    eat_now = TimeUtils.current_eat_time()
    target_time = eat_now.replace(hour=hour, minute=minute, second=0, microsecond=0)
    
    if eat_now > target_time:
        target_time += timedelta(days=1)
        
    delta = target_time - eat_now
    return delta.total_seconds()