import streamlit as st
import requests

st.set_page_config(page_title="BTC/USDT Futures P_micro (Gate.io)", layout="centered")
st.title("BTC/USDT Perpetual Futures P_micro Signal (Gate.io)")

CONTRACT = "BTC_USDT"  # Gate.io naming for BTC futures perpetual

def get_futures_order_book(contract=CONTRACT, limit=1):
    url = "https://fx-api.gateio.ws/api/v4/futures/usdt/order_book"
    params = {
        "contract": contract,
        "limit": limit  # top N levels; 1 for top-of-book
    }
    try:
        resp = requests.get(url, params=params, timeout=5)
        st.write("HTTP Status:", resp.status_code)
        data = resp.json()
        st.write("Raw response:", data)
        # Check for expected structure
        # Example successful response has 'bids' and 'asks'
        if 'bids' not in data or 'asks' not in data:
            st.error(f"Unexpected response format: {data}")
            return None, None, None, None

        best_bid = float(data['bids'][0][0])
        Qbid = float(data['bids'][0][1])
        best_ask = float(data['asks'][0][0])
        Qask = float(data['asks'][0][1])
        return best_bid, Qbid, best_ask, Qask
    except requests.exceptions.RequestException as e:
        st.error(f"Network error: {e}")
    except Exception as e:
        st.error(f"Data parsing error: {e}")
    return None, None, None, None

def compute_signal(A, Qbid, B, Qask):
    P_micro = (A * Qbid + B * Qask) / (Qbid + Qask)
    mid_price = (A + B) / 2
    if P_micro > mid_price:
        return P_micro, mid_price, "BUY"
    elif P_micro < mid_price:
        return P_micro, mid_price, "SELL"
    else:
        return P_micro, mid_price, "HOLD"

st.write(f"Fetching futures order book for {CONTRACT} on Gate.io...")

if st.button("Generate Signal"):
    A, Qbid, B, Qask = get_futures_order_book()
    if A is not None:
        P_micro, mid, signal = compute_signal(A, Qbid, B, Qask)
        st.write(f"Best Bid: {A}, Bid Vol: {Qbid}")
        st.write(f"Best Ask: {B}, Ask Vol: {Qask}")
        st.write(f"P_micro: {P_micro:.2f}")
        st.write(f"Mid Price: {mid:.2f}")
        st.write(f"Signal: {signal}")
    else:
        st.warning("Could not get order book — no signal generated.")