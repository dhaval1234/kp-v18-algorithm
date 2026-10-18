import datetime
import pandas as pd
import numpy as np

class KPv18AdvancedEngine:
    def __init__(self, symbol="NIFTY 50", account_size=100000, risk_per_trade_pct=1.0):
        self.symbol = symbol
        self.account_size = account_size
        self.risk_per_trade_pct = risk_per_trade_pct
        
        # Macro Planetary Vectors (-1 to +1)
        self.macro_saturn_retrograde = -1.0  # Saturn pressure
        self.macro_mars_position = -0.5     # Debilitated/Strained Mars

    def calculate_indicators(self, df):
        """
        Calculates RSI (20), VWAP, ATR (14), and Volume Moving Average
        """
        # RSI 20
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=20).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=20).mean()
        rs = gain / loss
        df['RSI_20'] = 100 - (100 / (1 + rs))

        # VWAP
        df['VWAP'] = (df['Volume'] * (df['High'] + df['Low'] + df['Close']) / 3).cumsum() / df['Volume'].cumsum()

        # ATR (Average True Range for Dynamic Stop Loss)
        high_low = df['High'] - df['Low']
        high_close = np.abs(df['High'] - df['Close'].shift())
        low_close = np.abs(df['Low'] - df['Close'].shift())
        ranges = pd.concat([high_low, high_close, low_close], axis=1)
        true_range = np.max(ranges, axis=1)
        df['ATR_14'] = true_range.rolling(14).mean()

        # Volume Spike Detector
        df['Vol_SMA20'] = df['Volume'].rolling(20).mean()
        df['Vol_Spike'] = df['Volume'] > (1.5 * df['Vol_SMA20'])

        return df

    def get_astro_weightage(self, nakshatra, tithi):
        """
        KP Micro-Transit Score Engine
        """
        nakshatra_bias = {
            "Swati": -0.8, "Jyeshtha": -0.6, "Mula": -0.9,
            "Purvashadha": 0.6, "Uttarashadha": 0.3, "Rohini": 0.8
        }
        tithi_bias = {
            "Nanda": 0.4, "Bhadra": 0.0, "Jaya": 0.6,
            "Rikta": -0.8, "Purna": 0.3
        }

        n_score = nakshatra_bias.get(nakshatra, 0.0)
        t_score = tithi_bias.get(tithi, 0.0)

        return n_score + t_score

    def get_hora_phase(self, current_time):
        """
        Hora Window Micro-Timing Matrix
        """
        time_str = current_time.strftime("%H:%M")
        if "09:15" <= time_str < "10:30":
            return "OPENING_PHASE", 1.2  # Higher volatility factor
        elif "10:30" <= time_str < "13:15":
            return "MID_PHASE", 0.8     # Lower volatility / consolidation
        elif "13:15" <= time_str <= "15:30":
            return "PRIME_PHASE", 1.5   # Directional trend acceleration
        return "OFF_MARKET", 0.0

    def calculate_position_size(self, entry_price, stop_loss):
        """
        Risk Management & Dynamic Position Sizing
        """
        risk_amount = self.account_size * (self.risk_per_trade_pct / 100.0)
        risk_per_share = abs(entry_price - stop_loss)
        if risk_per_share == 0:
            return 0
        quantity = int(risk_amount / risk_per_share)
        return quantity

    def evaluate_trade(self, price, rsi, vwap, atr, vol_spike, nakshatra, tithi, current_time):
        astro_micro = self.get_astro_weightage(nakshatra, tithi)
        hora_phase, hora_volatility = self.get_hora_phase(current_time)

        # Composite Astro-Tech Score
        composite_astro_score = self.macro_saturn_retrograde + self.macro_mars_position + astro_micro

        # Technical Status
        is_above_vwap = price > vwap
        is_overbought = rsi > 68
        is_oversold = rsi < 32

        signal = "NEUTRAL"
        confidence = "LOW"
        stop_loss = 0.0
        target = 0.0

        # High-Probability Bearish Setup (Macro Bearish + Overbought or VWAP Breakdown)
        if composite_astro_score <= -1.2:
            if is_overbought or (not is_above_vwap and vol_spike):
                signal = "SELL / SHORT"
                confidence = "HIGH" if hora_phase == "PRIME_PHASE" else "MEDIUM"
                stop_loss = price + (1.5 * atr)
                target = price - (3.0 * atr)  # 1:2 Risk-Reward

        # High-Probability Bullish / Liquidity Bounce Setup
        elif composite_astro_score >= 0.2 and is_above_vwap:
            if not is_overbought:
                signal = "BUY / LONG"
                confidence = "HIGH" if vol_spike else "MEDIUM"
                stop_loss = price - (1.5 * atr)
                target = price + (3.0 * atr)

        pos_qty = self.calculate_position_size(price, stop_loss) if signal != "NEUTRAL" else 0

        return {
            "Symbol": self.symbol,
            "Timestamp": current_time.strftime("%Y-%m-%d %H:%M:%S"),
            "Hora Window": hora_phase,
            "Astro Composite Score": round(composite_astro_score, 2),
            "RSI (20)": round(rsi, 2),
            "VWAP Status": "ABOVE" if is_above_vwap else "BELOW",
            "Volume Spike": "YES" if vol_spike else "NO",
            "Signal": signal,
            "Confidence": confidence,
            "Entry Price": price,
            "Suggested StopLoss": round(stop_loss, 2),
            "Suggested Target": round(target, 2),
            "Risk-Reward Ratio": "1:2",
            "Recommended Qty": pos_qty
        }

# ==========================================
# EXECUTION TEST
# ==========================================
if __name__ == "__main__":
    engine = KPv18AdvancedEngine(symbol="NIFTY 50", account_size=200000, risk_per_trade_pct=1.0)
    
    now = datetime.datetime.now()
    test_data = engine.evaluate_trade(
        price=23119.00,
        rsi=71.5,
        vwap=23050.00,
        atr=85.00,
        vol_spike=True,
        nakshatra="Swati",
        tithi="Rikta",
        current_time=now
    )

    print("\n================ KP v18 ENHANCED DEPLOYMENT MATRIX ================")
    for k, v in test_data.items():
        print(f"{k:<25}: {v}")
    print("===================================================================\n")