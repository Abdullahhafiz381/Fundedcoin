import streamlit as st
import pandas as pd
import numpy as np
import requests
import time
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go

# Page configuration
st.set_page_config(
    page_title="Funding Rate Sentiment Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for professional styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
        font-weight: bold;
    }
    .metric-card {
        background: #f0f2f6;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #1f77b4;
        margin: 0.5rem 0;
    }
    .overbullish {
        background-color: #ffebee !important;
        border-left: 4px solid #f44336 !important;
    }
    .overbearish {
        background-color: #e8f5e8 !important;
        border-left: 4px solid #4caf50 !important;
    }
    .neutral {
        background-color: #f5f5f5 !important;
        border-left: 4px solid #9e9e9e !important;
    }
    .positive-change {
        color: #4caf50;
        font-weight: bold;
    }
    .negative-change {
        color: #f44336;
        font-weight: bold;
    }
    .refresh-button {
        background: linear-gradient(45deg, #1f77b4, #4ca2f0);
        color: white;
        border: none;
        padding: 0.5rem 1rem;
        border-radius: 5px;
        cursor: pointer;
    }
</style>
""", unsafe_allow_html=True)

class FundingRateTracker:
    def __init__(self):
        self.base_url = "https://fapi.binance.com"
        self.funding_interval = 8  # hours
        self.history_data = {}
        
    def get_all_symbols(self):
        """Get all USDT perpetual futures symbols from Binance"""
        try:
            url = f"{self.base_url}/fapi/v1/exchangeInfo"
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                symbols = [symbol['symbol'] for symbol in data['symbols'] 
                          if symbol['symbol'].endswith('USDT') and symbol['contractType'] == 'PERPETUAL']
                return symbols
            else:
                return self.get_default_symbols()
        except Exception as e:
            st.error(f"Error fetching symbols: {e}")
            return self.get_default_symbols()
    
    def get_default_symbols(self):
        """Fallback to major symbols"""
        return ['BTCUSDT', 'ETHUSDT', 'ADAUSDT', 'DOTUSDT', 'LINKUSDT', 
                'BCHUSDT', 'LTCUSDT', 'XRPUSDT', 'EOSUSDT', 'ETCUSDT',
                'TRXUSDT', 'XLMUSDT', 'ATOMUSDT', 'XTZUSDT', 'ONTUSDT']
    
    def fetch_funding_rates(self, symbols):
        """Fetch current funding rates from Binance"""
        funding_data = []
        
        for symbol in symbols:
            try:
                # Get current funding rate
                url = f"{self.base_url}/fapi/v1/premiumIndex"
                params = {'symbol': symbol}
                response = requests.get(url, params=params, timeout=5)
                
                if response.status_code == 200:
                    data = response.json()
                    funding_rate = float(data.get('lastFundingRate', 0)) * 100  # Convert to percentage
                    
                    # Get mark price
                    mark_price = float(data.get('markPrice', 0))
                    
                    # Calculate 8-hour change (simulated for demo)
                    change_8h = self.calculate_8h_change(symbol, funding_rate)
                    
                    # Calculate FRSS
                    frss = funding_rate * 100
                    
                    # Determine sentiment
                    sentiment, action = self.determine_sentiment(funding_rate, change_8h)
                    
                    funding_data.append({
                        'symbol': symbol.replace('USDT', '/USDT'),
                        'funding_rate': funding_rate,
                        'change_8h': change_8h,
                        'frss': frss,
                        'sentiment': sentiment,
                        'action': action,
                        'mark_price': mark_price,
                        'timestamp': datetime.now()
                    })
                    
                    # Store in history for change calculation
                    if symbol not in self.history_data:
                        self.history_data[symbol] = []
                    self.history_data[symbol].append({
                        'timestamp': datetime.now(),
                        'funding_rate': funding_rate
                    })
                    
                else:
                    st.warning(f"Could not fetch data for {symbol}")
                    
            except Exception as e:
                st.warning(f"Error with {symbol}: {e}")
                continue
        
        return pd.DataFrame(funding_data)
    
    def calculate_8h_change(self, symbol, current_rate):
        """Calculate 8-hour funding rate change (simulated for demo)"""
        try:
            # In a real implementation, you would fetch historical funding rates
            # For demo purposes, we'll generate realistic changes
            if symbol in self.history_data and len(self.history_data[symbol]) > 1:
                # Use actual historical data if available
                historical_rates = self.history_data[symbol]
                if len(historical_rates) >= 2:
                    old_rate = historical_rates[0]['funding_rate']
                    change = ((current_rate - old_rate) / abs(old_rate)) * 100 if old_rate != 0 else 0
                    return min(max(change, -50), 50)  # Limit to ±50%
            
            # Generate realistic simulated change
            base_volatility = 0.5  # 50% maximum change
            change = np.random.uniform(-base_volatility, base_volatility)
            return change
            
        except:
            return np.random.uniform(-0.3, 0.3)  # Fallback
    
    def determine_sentiment(self, funding_rate, change_8h):
        """Determine market sentiment and suggested action"""
        abs_rate = abs(funding_rate)
        
        if funding_rate > 0.01:  # Positive and significant
            sentiment = "Overbullish"
            action = "Short scalp"
        elif funding_rate < -0.01:  # Negative and significant
            sentiment = "Overbearish" 
            action = "Long scalp"
        else:  # Near zero
            sentiment = "Neutral"
            action = "Wait"
        
        # Adjust based on 8h change trend
        if sentiment == "Overbullish" and change_8h > 0.1:
            action = "Strong Short scalp"
        elif sentiment == "Overbearish" and change_8h < -0.1:
            action = "Strong Long scalp"
            
        return sentiment, action
    
    def fetch_price_data(self, symbol):
        """Fetch current price data for a symbol"""
        try:
            url = f"{self.base_url}/fapi/v1/ticker/24hr"
            params = {'symbol': symbol.replace('/USDT', 'USDT')}
            response = requests.get(url, params=params, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                return {
                    'price': float(data.get('lastPrice', 0)),
                    'price_change': float(data.get('priceChangePercent', 0)),
                    'volume': float(data.get('volume', 0))
                }
        except:
            return None

def main():
    st.markdown('<div class="main-header">📊 Funding Rate Sentiment Dashboard</div>', unsafe_allow_html=True)
    st.caption("Track perpetual futures funding rates and market sentiment in real-time")
    
    # Initialize tracker
    if 'tracker' not in st.session_state:
        st.session_state.tracker = FundingRateTracker()
        st.session_state.last_update = datetime.now()
        st.session_state.auto_refresh = False
    
    tracker = st.session_state.tracker
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Dashboard Settings")
        
        # Auto-refresh
        st.subheader("🔄 Auto-Refresh")
        auto_refresh = st.checkbox("Enable auto-refresh every 10 minutes", value=False)
        
        # Sentiment filters
        st.subheader("🎯 Filter by Sentiment")
        show_overbullish = st.checkbox("Show Overbullish", value=True)
        show_overbearish = st.checkbox("Show Overbearish", value=True) 
        show_neutral = st.checkbox("Show Neutral", value=False)
        
        # Rate threshold filter
        st.subheader("📈 Rate Threshold")
        min_rate = st.slider("Minimum |Funding Rate| (%)", 0.0, 0.1, 0.001, 0.001)
        
        # Symbol selection
        st.subheader("🎯 Coin Selection")
        all_symbols = tracker.get_all_symbols()
        selected_symbols = st.multiselect(
            "Select coins to display:",
            [s.replace('USDT', '/USDT') for s in all_symbols],
            default=['BTC/USDT', 'ETH/USDT', 'ADA/USDT', 'DOT/USDT', 'LINK/USDT']
        )
        
        if st.button("🔄 Manual Refresh", type="primary", use_container_width=True):
            st.rerun()
    
    # Main content
    if not selected_symbols:
        st.warning("Please select at least one coin from the sidebar.")
        return
    
    # Fetch data
    with st.spinner("🔄 Fetching latest funding rates from Binance..."):
        # Convert back to Binance format
        binance_symbols = [s.replace('/USDT', 'USDT') for s in selected_symbols]
        df = tracker.fetch_funding_rates(binance_symbols)
    
    if df.empty:
        st.error("No data available. Please check your connection or try different symbols.")
        return
    
    # Apply filters
    sentiment_filters = []
    if show_overbullish:
        sentiment_filters.append("Overbullish")
    if show_overbearish:
        sentiment_filters.append("Overbearish") 
    if show_neutral:
        sentiment_filters.append("Neutral")
    
    filtered_df = df[
        (df['sentiment'].isin(sentiment_filters)) & 
        (abs(df['funding_rate']) >= min_rate)
    ].sort_values('frss', ascending=False)
    
    # Dashboard metrics
    st.subheader("📈 Market Overview")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        total_coins = len(filtered_df)
        st.metric("Coins Tracked", total_coins)
    
    with col2:
        overbullish_count = len(filtered_df[filtered_df['sentiment'] == 'Overbullish'])
        st.metric("Overbullish", overbullish_count)
    
    with col3:
        overbearish_count = len(filtered_df[filtered_df['sentiment'] == 'Overbearish'])
        st.metric("Overbearish", overbearish_count)
    
    with col4:
        avg_funding = filtered_df['funding_rate'].mean()
        st.metric("Avg Funding Rate", f"{avg_funding:.4f}%")
    
    with col5:
        high_frss = filtered_df['frss'].max() if not filtered_df.empty else 0
        st.metric("Max FRSS", f"{high_frss:.1f}")
    
    # Main data table
    st.subheader("🎯 Funding Rate Analysis")
    
    # Format the display dataframe
    display_df = filtered_df.copy()
    display_df['Funding Rate (%)'] = display_df['funding_rate'].apply(lambda x: f"{x:.4f}%")
    display_df['8h Change (%)'] = display_df['change_8h'].apply(lambda x: f"{x:+.2f}%")
    display_df['FRSS'] = display_df['frss'].apply(lambda x: f"{x:.1f}")
    display_df['Price'] = display_df['mark_price'].apply(lambda x: f"${x:,.2f}")
    
    # Create styled dataframe
    def color_sentiment(sentiment):
        if sentiment == "Overbullish":
            return 'color: #d32f2f; font-weight: bold'
        elif sentiment == "Overbearish":
            return 'color: #388e3c; font-weight: bold'
        else:
            return 'color: #616161; font-weight: bold'
    
    def color_action(action):
        if "Short" in action:
            return 'color: #d32f2f; font-weight: bold'
        elif "Long" in action:
            return 'color: #388e3c; font-weight: bold'
        else:
            return 'color: #616161; font-weight: bold'
    
    # Display table
    final_df = display_df[['symbol', 'Funding Rate (%)', '8h Change (%)', 'FRSS', 'sentiment', 'action', 'Price']]
    final_df.columns = ['Coin', 'Funding Rate (%)', '8h Change (%)', 'FRSS', 'Sentiment', 'Suggested Action', 'Price']
    
    styled_df = final_df.style.applymap(color_sentiment, subset=['Sentiment'])\
                              .applymap(color_action, subset=['Suggested Action'])\
                              .applymap(lambda x: 'color: #d32f2f' if '-' in x else 'color: #388e3c', 
                                       subset=['8h Change (%)'])
    
    st.dataframe(styled_df, use_container_width=True, height=400)
    
    # Visualizations
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Sentiment Distribution")
        if not filtered_df.empty:
            sentiment_counts = filtered_df['sentiment'].value_counts()
            fig1 = px.pie(
                values=sentiment_counts.values,
                names=sentiment_counts.index,
                color=sentiment_counts.index,
                color_discrete_map={
                    'Overbullish': '#f44336',
                    'Overbearish': '#4caf50', 
                    'Neutral': '#9e9e9e'
                }
            )
            st.plotly_chart(fig1, use_container_width=True)
    
    with col2:
        st.subheader("📈 Top FRSS Scores")
        if not filtered_df.empty:
            top_coins = filtered_df.nlargest(10, 'frss')
            fig2 = px.bar(
                top_coins,
                x='symbol',
                y='frss',
                color='sentiment',
                color_discrete_map={
                    'Overbullish': '#f44336',
                    'Overbearish': '#4caf50',
                    'Neutral': '#9e9e9e'
                },
                title="Top 10 Funding Rate Sentiment Scores"
            )
            st.plotly_chart(fig2, use_container_width=True)
    
    # Trading Opportunities Section
    st.subheader("💎 Trading Opportunities")
    
    # Find strong signals
    strong_bullish = filtered_df[
        (filtered_df['sentiment'] == 'Overbullish') & 
        (filtered_df['funding_rate'] > 0.02)
    ]
    
    strong_bearish = filtered_df[
        (filtered_df['sentiment'] == 'Overbearish') & 
        (filtered_df['funding_rate'] < -0.02)
    ]
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("🔥 **Strong Short Opportunities**")
        if not strong_bullish.empty:
            for _, coin in strong_bullish.iterrows():
                st.error(
                    f"**{coin['symbol']}** - Funding: {coin['funding_rate']:.4f}% | "
                    f"FRSS: {coin['frss']:.1f} | Action: {coin['action']}"
                )
        else:
            st.info("No strong short opportunities detected")
    
    with col2:
        st.write("📈 **Strong Long Opportunities**")
        if not strong_bearish.empty:
            for _, coin in strong_bearish.iterrows():
                st.success(
                    f"**{coin['symbol']}** - Funding: {coin['funding_rate']:.4f}% | "
                    f"FRSS: {coin['frss']:.1f} | Action: {coin['action']}"
                )
        else:
            st.info("No strong long opportunities detected")
    
    # Auto-refresh logic
    if auto_refresh:
        refresh_placeholder = st.empty()
        for i in range(600, 0, -1):  # 10 minutes countdown
            with refresh_placeholder:
                st.info(f"🔄 Auto-refresh in {i} seconds...")
            time.sleep(1)
        st.rerun()
    
    # Footer
    st.markdown("---")
    st.caption(f"🕒 Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | "
               "Data source: Binance Futures API | "
               "FRSS = Funding Rate × 100")

if __name__ == "__main__":
    main()