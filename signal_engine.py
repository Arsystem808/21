
from __future__ import annotations
import os
from datetime import datetime, timezone
import joblib

from src.data.data_hub import load_history_yf
from src.features.feature_engine import build_features

MODEL_PATH = "artifacts/lgbm_direction.pkl"

def soft_to_action(score: float) -> str:
    if score >= 0.6: return "BUY"
    if score <= 0.4: return "SHORT"
    return "WAIT"

def rationale_text(action: str) -> str:
    if action == "BUY":
        return "Покупатели удержали цену у поддержки, спрос подбирает — ждём проталкивание выше к целям."
    if action == "SHORT":
        return "Спрос выдыхается у сопротивления — ждём откат вниз к ближайшим уровням."
    return "Сигнал неочевиден: лучше дождаться ясного импульса."

def infer_score(latest_row, features) -> float:
    # Пытаемся загрузить модель, если её нет — возвращаем 0.5 (эвристика)
    if os.path.exists(MODEL_PATH):
        try:
            bundle = joblib.load(MODEL_PATH)
            model, feats = bundle.get("model"), bundle.get("features", features)
            return float(model.predict_proba(latest_row[feats])[:,1][0])
        except Exception:
            pass
    # fallback — мягкий ноль (середина)
    return 0.5

def build_signal(symbol: str, interval: str = "1d") -> dict:
    df = load_history_yf(symbol, period_years=3, interval=interval)
    feats = build_features(df)
    latest = feats.iloc[-1:]
    feature_cols = [c for c in feats.columns if c not in ("symbol","label")]
    score = infer_score(latest, feature_cols)
    action = soft_to_action(score)

    px = float(df['close'].iloc[-1])
    atr = float(latest['atr14'].iloc[-1])
    pivot = float(latest['pivot'].iloc[-1])
    r1 = float(latest['r1'].iloc[-1])
    s1 = float(latest['s1'].iloc[-1])

    if action == "BUY":
        entry = px
        tp1 = max(px + 0.6*atr, r1)
        tp2 = max(px + 1.2*atr, pivot + (r1 - pivot)*1.5)
        sl = px - 1.0*atr
    elif action == "SHORT":
        entry = px
        tp1 = min(px - 0.6*atr, s1)
        tp2 = min(px - 1.2*atr, pivot - (pivot - s1)*1.5)
        sl = px + 1.0*atr
    else:
        entry = px
        tp1 = px + 0.8*atr
        tp2 = px + 1.6*atr
        sl = px - 0.8*atr

    return {
        "symbol": symbol,
        "ts": datetime.now(timezone.utc).isoformat(),
        "horizon": "swing",
        "action": action,
        "entry": round(entry, 2),
        "tp": [round(tp1, 2), round(tp2, 2)],
        "sl": round(sl, 2),
        "confidence": round(score, 3),
        "rationale_text": rationale_text(action),
        "expiry_ts": None
    }
