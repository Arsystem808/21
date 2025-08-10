import os, sys, pathlib, importlib.util
import streamlit as st

# === 1) Добавим ./src в путь импорта ===
BASE_DIR = pathlib.Path(__file__).resolve().parent
SRC_DIR = BASE_DIR / "src"
if SRC_DIR.exists():
    sys.path.insert(0, str(SRC_DIR))

# === 2) Пытаемся импортировать как пакет ===
try:
    from src.common.config import get_config
except Exception:
    # === 3) Фоллбек: грузим модуль напрямую с файла src/common/config.py ===
    cfg_path = SRC_DIR / "common" / "config.py"
    if not cfg_path.exists():
        st.error(f"Не найден {cfg_path}. Проверь, что он в репозитории.")
        st.stop()
    spec = importlib.util.spec_from_file_location("capintel_config", str(cfg_path))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)  # type: ignore
    get_config = mod.get_config  # type: ignore

# === Дальше обычный код приложения ===
cfg = get_config()

st.set_page_config(page_title="AI Trading App", layout="wide")
st.title("AI Trading App — Test Load")
st.write("✅ Конфиг загружен:")
st.json(cfg)

# Ниже можешь вернуть основной UI (сигналы и т.д.)
