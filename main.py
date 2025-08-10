import sys, pathlib

# === Фикс путей, чтобы Python видел src/ ===
BASE_DIR = pathlib.Path(__file__).resolve().parent
SRC_DIR = BASE_DIR / "src"
if SRC_DIR.exists():
    sys.path.insert(0, str(SRC_DIR))

from src.common.config import get_config
import streamlit as st

# === Пример использования конфигурации ===
config = get_config()

st.set_page_config(page_title="AI Trading App", layout="wide")
st.title("AI Trading App — Test Load")

st.write("✅ Конфиг загружен:")
st.json(config)
