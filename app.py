import streamlit as st
import requests

st.set_page_config(page_title="BTC P_micro Signal", layout="centered")
st.title("BTC P_micro Signal Generator (Improved)")

# --- Config ---
SYMBOL = "BTCUSDT"
LIMIT = 5  # top 5 order book entries

# --- Fetch top-of-book BTC/USDT from Binance ---
def get_order_book(symbol=SYMBOL, limit=LIMIT):
    url = f"https://api.binance.com/api/v3/depth?symbol={symbol}&limit={limit}"
    try:
        response = requests.get(url, timeout=5)
        st.write(f"HTTP Status Code: {response.status_code}")  # Debug
        data = response.json()
        st.write("Raw Response:", data)  # Debug

        if "bids" not in data or "asks" not in data:
            st.error(f"Order book missing 'bids' or 'asks'. Full response: {data}")
            return None, None, None, None

        best_bid = float(data['bids'][0][0])
        Qbid = float(data['bids'][0][1])
        best_ask = float(data['asks'][0][0])
        Qask = float(data['asks'][0][1])
        return best_bid, Qbid, best_ask, Qask

    except requests.exceptions.RequestException as e:
        st.error(f"Network request failed: {e}")
    except ValueError as e:
        st.error(f"Error converting data: {e}")
    except Exception as e:
        st.error(f"Unexpected error: {e}")
    return None, None, None, None

# --- Compute P_micro and mid-price ---
def compute_signal(A, Qbid, B, Qask):
    P_micro = (A * Qbid + B * Qask) / (Qbid + Qask)
    mid_price = (A + B) / 2
    
    if P_micro > mid_price:
        signal = "BUY"
    elif P_micro < mid_price:
        signal = "SELL"
    else:
        signal = "HOLD"
    
    return P_micro, mid_price, signal

# --- Main ---
st.write(f"Fetching BTC/USDT order book (top {LIMIT}) from Binance...")

if st.button("Generate Signal"):
    A, Qbid, B, Qask = get_order_book()
    if A is not None and B is not None:
        P_micro, mid_price, signal = compute_signal(A, Qbid, B, Qask)
        st.write(f"**Best Bid (A):** {A} | **Volume at Bid:** {Qbid}")
        st.write(f"**Best Ask (B):** {B} | **Volume at Ask:** {Qask}")
        st.write(f"**P_micro:** {P_micro:.2f}")
        st.write(f"**Mid Price:** {mid_price:.2f}")
        st.write(f"**Signal:** {signal}")
    else:
        st.warning("Could not generate signal due to fetch error.")