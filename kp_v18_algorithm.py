import datetime
import pandas as pd
import numpy as np

# ==========================================
# KP v18 TRADING ALGORITHM CONFIGURATION
# ==========================================

class KPv18Predictor:
    def __init__(self, symbol="NIFTY"):
        self.symbol = symbol
        # Macro Planetary Vectors (1 = Bullish, -1 = Bearish, 0 = Neutral)
        self.macro_saturn_retrograde = -1  # Saturn Retrograde in Pisces
        self.macro_mars_debilitated = -1   # Mars Debilitated in Cancer

    def calculate_technical_indicators(self, df):
        """
        Calculate RSI (20) and VWAP for momentum validation
        """
        # RSI 20 Calculation
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=20).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=20).mean()
        rs = gain / loss
        df['RSI_20'] = 100 - (100 / (1 + rs))

        # VWAP Calculation
        df['VWAP'] = (df['Volume'] * (df['High'] + df['Low'] + df['Close']) / 3).cumsum() / df['Volume'].cumsum()
        return df

    def get_astrological_vectors(self, nakshatra, tithi):
        """
        KP v18 Micro-Transit Mapping Rules
        """
        # Nakshatra Weightage Mapping
        nakshatra_bias = {
            "Swati": -0.8,         # Rahu driven high volatility / bearish bias
            "Jyeshtha": -0.6,      # Mercury/Mars sudden turns
            "Mula": -0.9,          # Ketu deep profit booking
            "Purvashadha": 0.5,    # Venus liquidity bounce / short covering
            "Uttarashadha": 0.2    # Sun stability / rangebound
        }

        # Tithi Category Weightage
        tithi_bias = {
            "Nanda": 0.3,          # Happy/Growth
            "Bhadra": 0.0,          # Neutral/Consolidation
            "Jaya": 0.5,           # Victory/Bullish momentum
            "Rikta": -0.7,         # Empty/Sharp selling
            "Purna": 0.2           # Full/Completion
        }

        n_score = nakshatra_bias.get(nakshatra, 0.0)
        t_score = tithi_bias.get(tithi, 0.0)

        return n_score, t_score

    def evaluate_hora_window(self, current_time):
        """
        Hora Window Timing Engine (09:15 to 15:30)
        """
        time_str = current_time.strftime("%H:%M")
        
        if "09:15" <= time_str < "10:30":
            return "OPENING_PHASE", "High Volatility / Initial Momentum"
        elif "10:30" <= time_str < "13:15":
            return "MID_PHASE", "Consolidation / Range Formation"
        elif "13:15" <= time_str <= "15:30":
            return "PRIME_PHASE", "Trend Acceleration / Macro Realization"
        else:
            return "OFF_MARKET", "Market Closed"

    def generate_signal(self, current_price, rsi_20, vwap, nakshatra, tithi, current_time):
        """
        Final KP v18 Decision Engine
        """
        n_score, t_score = self.get_astrological_vectors(nakshatra, tithi)
        hora_phase, hora_desc = self.evaluate_hora_window(current_time)

        # Macro Astro Score (-2.0 to +2.0)
        astro_score = self.macro_saturn_retrograde + self.macro_mars_debilitated + n_score + t_score

        # Technical Filters
        is_above_vwap = current_price > vwap
        is_overbought = rsi_20 > 70
        is_oversold = rsi_20 < 30

        # Decision Matrix
        strategy = "NEUTRAL / WAIT"
        confidence = "MEDIUM"

        # Sell on Rise Setup (Macro Bearish + Overbought RSI)
        if astro_score < -1.0:
            if is_overbought or (is_above_vwap and hora_phase == "PRIME_PHASE"):
                strategy = "SELL ON RISE (SHORT)"
                confidence = "HIGH"
            elif not is_above_vwap:
                strategy = "BEARISH CONTINUATION"
                confidence = "HIGH"

        # Counter-Trend / Liquidity Bounce (e.g. Purvashadha)
        elif astro_score >= 0 and is_above_vwap:
            strategy = "SHORT COVERING / TACTICAL LONG"
            confidence = "MEDIUM"

        return {
            "Symbol": self.symbol,
            "Timestamp": current_time.strftime("%Y-%m-%d %H:%M:%S"),
            "Hora Phase": hora_phase,
            "Astro Score": round(astro_score, 2),
            "RSI (20)": round(rsi_20, 2),
            "Price vs VWAP": "ABOVE" if is_above_vwap else "BELOW",
            "Recommended Strategy": strategy,
            "Confidence": confidence
        }

# ==========================================
# EXECUTION / TESTING
# ==========================================
if __name__ == "__main__":
    predictor = KPv18Predictor(symbol="NIFTY 50")
    
    # Mock Market Data for Testing
    now = datetime.datetime.now()
    test_price = 23119.00
    test_rsi = 61.73
    test_vwap = 23007.19
    current_nakshatra = "Purvashadha"
    current_tithi = "Jaya"

    decision = predictor.generate_signal(
        current_price=test_price,
        rsi_20=test_rsi,
        vwap=test_vwap,
        nakshatra=current_nakshatra,
        tithi=current_tithi,
        current_time=now
    )

    print("\n================ KP v18 DEPLOYMENT MATRIX ================")
    for key, value in decision.items():
        print(f"{key}: {value}")
    print("==========================================================\n")