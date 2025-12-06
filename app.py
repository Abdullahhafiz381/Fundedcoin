import streamlit as st
import requests

st.set_page_config(page_title="BTC-USDT Futures P_micro (OKX)", layout="centered")
st.title("BTC-USDT Futures P_micro Signal (OKX)")

INST_ID = "BTC-USDT-SWAP"  # OKX perpetual futures instrument id
DEPTH = 1  # fetch only top-of-book

def get_order_book(instId=INST_ID, depth=DEPTH):
    url = "https://www.okx.com/api/v5/market/books"
    params = {"instId": instId, "sz": depth}
    try:
        r = requests.get(url, params=params, timeout=5)
        st.write("HTTP Status:", r.status_code)
        data = r.json()
        st.write("Raw response:", data)
        # data["data"] is a list: first element has 'bids' and 'asks'
        if not data.get("data"):
            st.error("No data in response")
            return None, None, None, None

        entry = data["data"][0]
        bids = entry.get("bids", [])
        asks = entry.get("asks", [])
        if not bids or not asks:
            st.error("No bids or asks in order book")
            return None, None, None, None

        best_bid = float(bids[0][0])
        Qbid     = float(bids[0][1])
        best_ask = float(asks[0][0])
        Qask     = float(asks[0][1])
        return best_bid, Qbid, best_ask, Qask

    except Exception as e:
        st.error(f"Error fetching/parsing order book: {e}")
        return None, None, None, None

def compute_signal(A, Qbid, B, Qask):
    P_micro = (A * Qbid + B * Qask) / (Qbid + Qask)
    mid_price = (A + B) / 2
    if P_micro > mid_price:
        return "BUY", P_micro, mid_price
    elif P_micro < mid_price:
        return "SELL", P_micro, mid_price
    else:
        return "HOLD", P_micro, mid_price

st.write(f"Fetching order book for {INST_ID} ...")

if st.button("Generate Signal"):
    A, Qbid, B, Qask = get_order_book()
    if A is not None:
        signal, P_micro, mid = compute_signal(A, Qbid, B, Qask)
        st.write(f"Best Bid: {A}  |  Bid Qty: {Qbid}")
        st.write(f"Best Ask: {B}  |  Ask Qty: {Qask}")
        st.write(f"P_micro: {P_micro:.2f}")
        st.write(f"Mid Price: {mid:.2f}")
        st.write(f"Signal: {signal}")
    else:
        st.warning("Could not fetch valid order book — no signal generated.")