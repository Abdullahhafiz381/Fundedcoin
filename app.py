import streamlit as st
import requests

st.set_page_config(page_title="BTC Futures P_micro Signal", layout="centered")
st.title("BTC Perpetual Futures P_micro Signal Generator (Bybit)")

SYMBOL = "BTCUSDT"

def get_futures_order_book(symbol=SYMBOL):
    url = f"https://api.bybit.com/v2/public/orderBook/L2?symbol={symbol}"
    try:
        response = requests.get(url, timeout=5)
        st.write("HTTP Status:", response.status_code)
        data = response.json()
        st.write("Raw response:", data)

        if data.get("ret_code") != 0:
            st.error(f"Failed to fetch order book. Response: {data}")
            return None, None, None, None

        bids = [item for item in data["result"] if item["side"] == "Buy"]
        asks = [item for item in data["result"] if item["side"] == "Sell"]

        if not bids or not asks:
            st.error(f"No bids or asks in response: {data}")
            return None, None, None, None

        # Top-of-book
        best_bid = float(bids[0]["price"])
        Qbid = float(bids[0]["size"])
        best_ask = float(asks[0]["price"])
        Qask = float(asks[0]["size"])
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

st.write(f"Fetching BTC/USDT perpetual futures order book from Bybit...")

if st.button("Generate Signal"):
    A, Qbid, B, Qask = get_futures_order_book()
    if A is not None and B is not None:
        P_micro, mid_price, signal = compute_signal(A, Qbid, B, Qask)
        st.write(f"Best Bid: {A} | Bid Volume: {Qbid}")
        st.write(f"Best Ask: {B} | Ask Volume: {Qask}")
        st.write(f"P_micro: {P_micro:.2f}")
        st.write(f"Mid Price: {mid_price:.2f}")
        st.write(f"Signal: {signal}")
    else:
        st.warning("Could not generate signal — order book fetch error.")