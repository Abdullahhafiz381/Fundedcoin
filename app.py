import streamlit as st
import requests

st.set_page_config(page_title="BTC P_micro Signal (Bybit)", layout="centered")
st.title("BTC P_micro Signal Generator (Bybit)")

# Config
SYMBOL = "BTCUSDT"
CATEGORY = "spot"
LIMIT = 1  # top level size (you can try 5 or more if available)

# Fetch order book from Bybit REST API
def get_order_book(symbol=SYMBOL, category=CATEGORY, limit=LIMIT):
    url = "https://api.bybit.com/v5/market/orderbook"
    params = {
        "symbol": symbol,
        "category": category,
        "limit": limit
    }
    try:
        response = requests.get(url, params=params, timeout=5)
        st.write("HTTP Status:", response.status_code)  # debug
        data = response.json()
        st.write("Raw response:", data)  # debug

        # Bybit returns data under "result" key
        result = data.get("result")
        if not result:
            st.error(f"No result in response: {data}")
            return None, None, None, None

        bids = result.get("list")[0].get("bids")
        asks = result.get("list")[0].get("asks")
        if not bids or not asks:
            st.error(f"No bids or asks in result: {result}")
            return None, None, None, None

        best_bid = float(bids[0][0])
        Qbid = float(bids[0][1])
        best_ask = float(asks[0][0])
        Qask = float(asks[0][1])
        return best_bid, Qbid, best_ask, Qask

    except requests.exceptions.RequestException as e:
        st.error(f"Network error: {e}")
    except Exception as e:
        st.error(f"Error parsing data: {e}")

    return None, None, None, None

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

st.write(f"Fetching order book for {SYMBOL} from Bybit...")

if st.button("Generate Signal"):
    A, Qbid, B, Qask = get_order_book()
    if A is not None and B is not None:
        P_micro, mid_price, signal = compute_signal(A, Qbid, B, Qask)
        st.write(f"Best Bid: {A} | Bid Volume: {Qbid}")
        st.write(f"Best Ask: {B} | Ask Volume: {Qask}")
        st.write(f"P_micro: {P_micro:.2f}")
        st.write(f"Mid Price: {mid_price:.2f}")
        st.write(f"Signal: {signal}")
    else:
        st.warning("Could not generate signal — order book fetch error.")