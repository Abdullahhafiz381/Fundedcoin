import streamlit as st
import requests

st.set_page_config(page_title="BTC Spot P_micro Signal", layout="centered")
st.title("BTC Spot P_micro Signal Generator (KuCoin)")

SYMBOL = "BTC-USDT"

def get_spot_order_book(symbol=SYMBOL):
    url = f"https://api.kucoin.com/api/v1/market/orderbook/level2_100?symbol={symbol}"
    try:
        response = requests.get(url, timeout=5)
        st.write("HTTP Status:", response.status_code)
        data = response.json()
        st.write("Raw response:", data)

        if data.get("code") != "200000":
            st.error(f"Failed to fetch order book. Response: {data}")
            return None, None, None, None

        bids = data["data"]["bids"]
        asks = data["data"]["asks"]

        if not bids or not asks:
            st.error(f"No bids or asks in response: {data}")
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

st.write(f"Fetching BTC/USDT spot order book from KuCoin...")

if st.button("Generate Signal"):
    A, Qbid, B, Qask = get_spot_order_book()
    if A is not None and B is not None:
        P_micro, mid_price, signal = compute_signal(A, Qbid, B, Qask)
        st.write(f"Best Bid: {A} | Bid Volume: {Qbid}")
        st.write(f"Best Ask: {B} | Ask Volume: {Qask}")
        st.write(f"P_micro: {P_micro:.2f}")
        st.write(f"Mid Price: {mid_price:.2f}")
        st.write(f"Signal: {signal}")
    else:
        st.warning("Could not generate signal — order book fetch error.")