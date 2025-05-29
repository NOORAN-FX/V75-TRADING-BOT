import pandas_ta as ta
import pandas as pd
import pytz
from datetime import datetime

class AnalysisEngine:
    def __init__(self):
        self.candles = pd.DataFrame()
        self.trend = "Neutral"
        self.volatility = "Normal"

    def process_candles(self, candles):
        self.candles = candles
        self._calculate_indicators()
        self._determine_trend()
        self._check_volatility()

    def _calculate_indicators(self):
        # Calculate technical indicators
        self.candles['EMA50'] = ta.ema(self.candles['close'], length=50)
        self.candles['EMA200'] = ta.ema(self.candles['close'], length=200)
        macd = ta.macd(self.candles['close'], fast=12, slow=26, signal=9)
        self.candles['MACD_line'] = macd['MACD_12_26_9']
        self.candles['MACD_signal'] = macd['MACDs_12_26_9']
        self.candles['RSI'] = ta.rsi(self.candles['close'], length=14)
        bbands = ta.bbands(self.candles['close'], length=20, std=2)
        self.candles['BB_upper'] = bbands['BBU_20_2.0']
        self.candles['BB_lower'] = bbands['BBL_20_2.0']

    def _determine_trend(self):
        last_row = self.candles.iloc[-1]
        
        if (last_row['EMA50'] > last_row['EMA200'] and
            last_row['MACD_line'] > last_row['MACD_signal'] and
            last_row['RSI'] > 60):
            self.trend = "Bullish"
        elif (last_row['EMA50'] < last_row['EMA200'] and
              last_row['MACD_line'] < last_row['MACD_signal'] and
              last_row['RSI'] < 40):
            self.trend = "Bearish"
        else:
            self.trend = "Neutral"

    def _check_volatility(self):
        avg_range = (self.candles['high'] - self.candles['low']).mean()
        self.volatility = "High" if avg_range > 250 else "Normal"

    def make_prediction(self):
        eat_time = datetime.now(pytz.timezone('Africa/Nairobi'))
        # Allow predictions in testing mode
        if os.getenv('TESTING_MODE') != '1':
            if not (11 <= eat_time.hour <= 12 and eat_time.minute == 59):
                return None

        pa_signal = self._check_price_action()
        confidence = self._calculate_confidence()
        
        prediction = {
            "confidence": confidence,
            "duration": self._recommend_duration(confidence),
            "factors": {
                "trend": self.trend,
                "volatility": self.volatility,
                "price_action": pa_signal,
                "rsi": float(self.candles['RSI'].iloc[-1]),
                "macd_diff": float(self.candles['MACD_line'].iloc[-1] - self.candles['MACD_signal'].iloc[-1])
            }
        }

        if "Strong" in pa_signal and self.volatility == "High":
            prediction["direction"] = "Rise" if "Bullish" in pa_signal else "Fall"
        elif confidence >= 70:
            prediction["direction"] = "Rise" if self.trend == "Bullish" else "Fall"
        else:
            prediction["direction"] = "No Trade"
        
        return prediction

    def _check_price_action(self):
        # Analyze last 10 candles for stronger price action signals
        recent = self.candles[-10:]
        
        # Check for consecutive higher highs/lows
        hh_hl = sum(1 for i in range(1, len(recent)) 
                   if recent['high'].iloc[i] > recent['high'].iloc[i-1] 
                   and recent['low'].iloc[i] > recent['low'].iloc[i-1])
        
        # Check for consecutive lower highs/lows
        lh_ll = sum(1 for i in range(1, len(recent)) 
                   if recent['high'].iloc[i] < recent['high'].iloc[i-1] 
                   and recent['low'].iloc[i] < recent['low'].iloc[i-1])
        
        # Check Bollinger Band proximity
        last_close = recent['close'].iloc[-1]
        bb_width = recent['BB_upper'].iloc[-1] - recent['BB_lower'].iloc[-1]
        
        if hh_hl >= 6 and last_close > recent['BB_upper'].iloc[-2]:
            return "Strong Bullish"
        elif lh_ll >= 6 and last_close < recent['BB_lower'].iloc[-2]:
            return "Strong Bearish"
        elif hh_hl > lh_ll:
            return "Bullish"
        elif lh_ll > hh_hl:
            return "Bearish"
        return "Neutral"

    def _calculate_confidence(self):
        # Weighted confidence calculation
        factors = {
            'ema_crossover': 30 if self.trend != "Neutral" else 0,
            'macd': 20 if (self.candles['MACD_line'].iloc[-1] > self.candles['MACD_signal'].iloc[-1]) == (self.trend == "Bullish") else 0,
            'rsi': min(max((self.candles['RSI'].iloc[-1] - 40) / 20 * 15, 0), 15) if self.trend == "Bullish" else 
                   min(max((60 - self.candles['RSI'].iloc[-1]) / 20 * 15, 0), 15),
            'volatility': 15 if self.volatility == "High" else 5,
            'bb_proximity': 10 if (self.candles['close'].iloc[-1] > self.candles['BB_upper'].iloc[-1] and self.trend == "Bullish") or 
                                  (self.candles['close'].iloc[-1] < self.candles['BB_lower'].iloc[-1] and self.trend == "Bearish") else 0
        }
        return min(int(sum(factors.values())), 100)

    def _recommend_duration(self):
        return "1 hour" if self.volatility == "High" else "30 minutes"