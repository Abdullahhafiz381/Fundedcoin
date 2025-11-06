streamlit_funding_rate_dashboard.py

Funding Rate Sentiment Dashboard (Binance Futures) — Streamlit app

Notes:

- Uses Binance Futures public REST endpoints to fetch funding rates.

- No API key required.

- Keep an eye on Binance rate limits if you request many symbols frequently.

import time from typing import List, Dict

import pandas as pd import requests import streamlit as st

BASE_BINANCE = "https://fapi.binance.com"

st.set_page_config(page_title="Funding Rate Scanner", layout="wide") st.title("Funding Rate Sentiment Scanner — Binance Futures") st.markdown("A quick dashboard to scan perpetual futures funding rates and pick scalp candidates.")

--- Utility functions ---

@st.cache_data(ttl=60) def fetch_exchange_info() -> Dict: url = f"{BASE_BINANCE}/fapi/v1/exchangeInfo" r = requests.get(url, timeout=10) r.raise_for_status() return r.json()

@st.cache_data(ttl=15) def fetch_latest_funding(symbol: str) -> Dict: """Return the most recent funding record for a symbol. Uses limit=1.""" url = f"{BASE_BINANCE}/fapi/v1/fundingRate" params = {"symbol": symbol, "limit": 1} r = requests.get(url, params=params, timeout=10) r.raise_for_status() data = r.json() if isinstance(data, list) and len(data) > 0: return data[0] return {}

def build_symbol_list() -> List[str]: info = fetch_exchange_info() symbols = [] for s in info.get("symbols", []): # We want perp USDT-margined contracts. Filter common patterns. sym = s.get("symbol") contract_type = s.get("contractType") or s.get("contractType", "") # Many exchanges show USDT perpetuals as symbols ending with 'USDT'. if not sym: continue if sym.endswith("USDT"): symbols.append(sym) # Deduplicate and sort symbols = sorted(list(set(symbols))) return symbols

--- Sidebar controls ---

st.sidebar.header("Scanner settings") max_symbols = st.sidebar.slider("Max symbols to scan", 10, 200, 60, step=10) fr_threshold = st.sidebar.number_input("FR threshold (absolute, %)", min_value=0.001, max_value=5.0, value=0.05, step=0.01) refresh_secs = st.sidebar.slider("Auto-refresh (seconds)", 0, 300, 0, step=5) show_only = st.sidebar.selectbox("Show only", ["All", "Overbullish (>threshold)", "Overbearish (<-threshold)"]) sort_by = st.sidebar.selectbox("Sort by", ["abs_fr", "fundingRate", "symbol"])

st.sidebar.markdown("---") st.sidebar.markdown("Developer notes: Uses Binance /fapi/v1/fundingRate (limit=1). Avoid setting very low auto-refresh with many symbols to stay within rate limits.")

--- Main logic ---

symbols = build_symbol_list() symbols = symbols[:max_symbols]

if st.sidebar.button("Refresh now"): # clear caches fetch_latest_funding.clear() fetch_exchange_info.clear()

progress = st.progress(0) rows = [] for i, sym in enumerate(symbols): try: rec = fetch_latest_funding(sym) except Exception as e: rec = {} funding_rate = float(rec.get("fundingRate", 0.0)) if rec else 0.0 next_funding_time = rec.get("fundingTime") if rec else None # FRSS = funding_rate * 100 frss = funding_rate * 100 rows.append({ "symbol": sym, "fundingRate": funding_rate, "FRSS_%": frss, "nextFundingTime": next_funding_time, "raw": rec, "abs_fr": abs(frss), }) # update progress if max_symbols > 0: progress.progress((i + 1) / len(symbols))

if len(rows) == 0: st.warning("No symbols found or API failed. Try refresh or reduce the max symbols.") st.stop()

df = pd.DataFrame(rows)

classification

threshold = float(fr_threshold)

def classify(fr): if fr > threshold: return "Overbullish" if fr < -threshold: return "Overbearish" return "Neutral"

df["sentiment"] = df["FRSS_%"].apply(classify)

filters

if show_only != "All": if "Overbullish" in show_only: df = df[df.sentiment == "Overbullish"] elif "Overbearish" in show_only: df = df[df.sentiment == "Overbearish"]

sorting

if sort_by == "abs_fr": df = df.sort_values("abs_fr", ascending=False) elif sort_by == "fundingRate": df = df.sort_values("fundingRate", ascending=False) else: df = df.sort_values("symbol")

Display table

st.subheader(f"Scanned symbols: {len(df)} (threshold ±{threshold}%)")

Highlight styling

def highlight_row(r): if r.sentiment == "Overbullish": return ["background-color: #ffdede"] * len(r) if r.sentiment == "Overbearish": return ["background-color: #e6ffd9"] * len(r) return [""] * len(r)

st.dataframe(df[["symbol", "fundingRate", "FRSS_%", "sentiment"]].rename(columns={"FRSS_%": "FRSS (%)", "fundingRate": "fundingRate (raw)"}), height=600)

Quick action area

st.markdown("---") col1, col2 = st.columns([1, 2]) with col1: st.write("Top candidates") top = df.head(10) st.table(top[["symbol", "FRSS_%", "sentiment"]].set_index("symbol")) with col2: st.write("How to use") st.markdown( """

Overbullish (FRSS > threshold): crowd is long -> consider short scalp setups if price structure supports it.

Overbearish (FRSS < -threshold): crowd is short -> consider long scalp setups.

Always confirm with price action, volume and liquidity zones before entering.

Avoid using very large position sizes — this is a sentiment scanner not a signal generator. """ )


Auto refresh logic (client-side)

if refresh_secs > 0: st.experimental_rerun()

st.markdown("---") st.caption("Notes: Uses Binance public endpoints. If you need more features (websocket, Coinglass aggregated FR, historical averaging), I can extend this.")