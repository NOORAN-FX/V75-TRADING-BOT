import pandas as pd
import numpy as np

class PriceActionAnalyzer:
    def __init__(self, candles):
        self.candles = candles
        self.recent = candles[-10:]

    def detect_order_blocks(self):
        blocks = []
        for i in range(2, len(self.recent)-2):
            if self._is_bullish_block(i):
                blocks.append({'type': 'bullish', 'index': i})
            elif self._is_bearish_block(i):
                blocks.append({'type': 'bearish', 'index': i})
        return blocks

    def _is_bullish_block(self, index):
        candle = self.recent.iloc[index]
        prev1 = self.recent.iloc[index-1]
        prev2 = self.recent.iloc[index-2]
        return candle['close'] > prev1['high'] and prev1['close'] > prev2['high']

    def _is_bearish_block(self, index):
        candle = self.recent.iloc[index]
        prev1 = self.recent.iloc[index-1]
        prev2 = self.recent.iloc[index-2]
        return candle['close'] < prev1['low'] and prev1['close'] < prev2['low']

    def market_structure(self):
        highs = self.recent['high']
        lows = self.recent['low']
        
        hh = all(np.diff(highs.dropna()) > 0)
        hl = all(np.diff(lows.dropna()) > 0)
        lh = all(np.diff(highs.dropna()) < 0)
        ll = all(np.diff(lows.dropna()) < 0)

        if hh and hl:
            return 'HH/HL'
        elif lh and ll:
            return 'LH/LL'
        return 'Neutral'

    def detect_imbalances(self):
        imbalances = []
        for i in range(1, len(self.recent)-1):
            curr = self.recent.iloc[i]
            next = self.recent.iloc[i+1]
            
            if curr['high'] < next['low']:
                imbalances.append({'type': 'bullish', 'index': i})
            elif curr['low'] > next['high']:
                imbalances.append({'type': 'bearish', 'index': i})
        return imbalances