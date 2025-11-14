import streamlit as st
import requests
import pandas as pd
import json
import os
from datetime import datetime, timedelta
import plotly.graph_objects as go
import plotly.express as px

# GODZILLERS Streamlit setup
st.set_page_config(
    page_title="🔥 GODZILLERS CRYPTO TRACKER",
    page_icon="🐲",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# GODZILLERS CSS with red and black theme
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;500;700;900&family=Rajdhani:wght@300;400;500;600;700&display=swap');
    
    .main {
        background: linear-gradient(135deg, #000000 0%, #1a0000 50%, #330000 100%);
        color: #ffffff;
        font-family: 'Rajdhani', sans-serif;
    }
    
    .stApp {
        background: linear-gradient(135deg, #000000 0%, #1a0000 50%, #330000 100%);
    }
    
    .godzillers-header {
        background: linear-gradient(90deg, #ff0000 0%, #ff4444 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-family: 'Orbitron', monospace;
        font-weight: 900;
        text-align: center;
        font-size: 4rem;
        margin-bottom: 0.5rem;
        text-shadow: 0 0 30px rgba(255, 0, 0, 0.7);
        letter-spacing: 3px;
    }
    
    .godzillers-subheader {
        color: #ff6666;
        font-family: 'Orbitron', monospace;
        text-align: center;
        font-size: 1.4rem;
        margin-bottom: 2rem;
        letter-spacing: 3px;
        text-transform: uppercase;
    }
    
    .godzillers-card {
        background: rgba(20, 0, 0, 0.9);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 0, 0, 0.5);
        border-radius: 15px;
        padding: 1.5rem;
        margin: 0.5rem 0;
        box-shadow: 0 8px 32px rgba(255, 0, 0, 0.3);
        transition: all 0.3s ease;
    }
    
    .godzillers-card:hover {
        border-color: #ff4444;
        box-shadow: 0 8px 32px rgba(255, 0, 0, 0.5);
        transform: translateY(-2px);
    }
    
    .signal-buy {
        background: linear-gradient(135deg, rgba(0, 255, 0, 0.1) 0%, rgba(0, 100, 0, 0.3) 100%);
        border: 1px solid #00ff00;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 0.5rem 0;
        box-shadow: 0 0 20px rgba(0, 255, 0, 0.3);
    }
    
    .signal-sell {
        background: linear-gradient(135deg, rgba(255, 0, 0, 0.2) 0%, rgba(100, 0, 0, 0.4) 100%);
        border: 1px solid #ff0000;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 0.5rem 0;
        box-shadow: 0 0 20px rgba(255, 0, 0, 0.4);
    }
    
    .signal-neutral {
        background: linear-gradient(135deg, rgba(255, 165, 0, 0.1) 0%, rgba(100, 65, 0, 0.3) 100%);
        border: 1px solid #ffa500;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 0.5rem 0;
        box-shadow: 0 0 20px rgba(255, 165, 0, 0.3);
    }
    
    .price-glow {
        background: linear-gradient(135deg, rgba(255, 0, 0, 0.15) 0%, rgba(139, 0, 0, 0.25) 100%);
        border: 1px solid rgba(255, 0, 0, 0.6);
        border-radius: 15px;
        padding: 2rem;
        margin: 1rem 0;
        box-shadow: 0 0 40px rgba(255, 0, 0, 0.4);
        position: relative;
        overflow: hidden;
    }
    
    .price-glow::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: linear-gradient(45deg, transparent, rgba(255, 0, 0, 0.1), transparent);
        animation: shine 3s infinite linear;
    }
    
    @keyframes shine {
        0% { transform: translateX(-100%) translateY(-100%) rotate(45deg); }
        100% { transform: translateX(100%) translateY(100%) rotate(45deg); }
    }
    
    .godzillers-button {
        background: linear-gradient(90deg, #ff0000 0%, #cc0000 100%);
        border: none;
        border-radius: 25px;
        color: #000000;
        font-family: 'Orbitron', monospace;
        font-weight: 700;
        padding: 0.75rem 2rem;
        transition: all 0.3s ease;
        box-shadow: 0 0 20px rgba(255, 0, 0, 0.5);
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    .godzillers-button:hover {
        background: linear-gradient(90deg, #ff4444 0%, #ff0000 100%);
        transform: scale(1.05);
        box-shadow: 0 0 30px rgba(255, 0, 0, 0.7);
        color: #000000;
    }
    
    .metric-godzillers {
        background: rgba(0, 0, 0, 0.7);
        border: 1px solid rgba(255, 0, 0, 0.3);
        border-radius: 10px;
        padding: 1rem;
        margin: 0.5rem 0;
    }
    
    .trademark {
        text-align: center;
        color: #ff6666;
        font-family: 'Orbitron', monospace;
        font-size: 0.9rem;
        margin-top: 2rem;
        letter-spacing: 2px;
        text-transform: uppercase;
    }
    
    .section-header {
        font-family: 'Orbitron', monospace;
        font-size: 2rem;
        background: linear-gradient(90deg, #ff0000 0%, #ff4444 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 2rem 0 1rem 0;
        text-shadow: 0 0 20px rgba(255, 0, 0, 0.5);
        text-transform: uppercase;
        letter-spacing: 2px;
    }
    
    .divider {
        height: 3px;
        background: linear-gradient(90deg, transparent 0%, #ff0000 50%, transparent 100%);
        margin: 2rem 0;
    }
    
    .pulse {
        animation: pulse 2s infinite;
    }
    
    @keyframes pulse {
        0% { opacity: 1; }
        50% { opacity: 0.7; }
        100% { opacity: 1; }
    }
    
    .coin-card {
        background: rgba(30, 0, 0, 0.9);
        border: 1px solid rgba(255, 0, 0, 0.3);
        border-radius: 12px;
        padding: 1rem;
        margin: 0.5rem;
        transition: all 0.3s ease;
    }
    
    .coin-card:hover {
        border-color: #ff0000;
        box-shadow: 0 0 20px rgba(255, 0, 0, 0.4);
        transform: translateY(-3px);
    }
    
    .fire-effect {
        background: linear-gradient(45deg, #ff0000, #ff4400, #ff0000);
        background-size: 200% 200%;
        animation: fire 2s ease infinite;
    }
    
    @keyframes fire {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    .alert-banner {
        background: linear-gradient(90deg, #ff0000, #cc0000);
        border: 2px solid #ff4444;
        border-radius: 10px;
        padding: 1rem;
        margin: 1rem 0;
        box-shadow: 0 0 20px rgba(255, 0, 0, 0.5);
        animation: pulse 2s infinite;
    }
    
    /* Login Page Styles */
    .login-container {
        display: flex;
        justify-content: center;
        align-items: center;
        min-height: 100vh;
        background: linear-gradient(135deg, #000000 0%, #1a0000 50%, #330000 100%);
        padding: 20px;
    }
    
    .login-card {
        background: rgba(20, 0, 0, 0.95);
        backdrop-filter: blur(10px);
        border: 2px solid rgba(255, 0, 0, 0.6);
        border-radius: 20px;
        padding: 3rem;
        width: 100%;
        max-width: 450px;
        box-shadow: 0 0 50px rgba(255, 0, 0, 0.5);
        text-align: center;
    }
    
    .login-header {
        background: linear-gradient(90deg, #ff0000 0%, #ff4444 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-family: 'Orbitron', monospace;
        font-weight: 900;
        font-size: 2.5rem;
        margin-bottom: 1rem;
        text-shadow: 0 0 20px rgba(255, 0, 0, 0.7);
    }
    
    .login-subheader {
        color: #ff6666;
        font-family: 'Orbitron', monospace;
        font-size: 1rem;
        margin-bottom: 2rem;
        letter-spacing: 2px;
    }
    
    .login-input {
        background: rgba(0, 0, 0, 0.8);
        border: 1px solid rgba(255, 0, 0, 0.5);
        border-radius: 10px;
        color: white;
        font-family: 'Rajdhani', sans-serif;
        padding: 0.75rem 1rem;
        margin: 0.5rem 0;
        width: 100%;
        font-size: 1rem;
    }
    
    .login-input:focus {
        outline: none;
        border-color: #ff0000;
        box-shadow: 0 0 10px rgba(255, 0, 0, 0.5);
    }
    
    .login-button {
        background: linear-gradient(90deg, #ff0000 0%, #cc0000 100%);
        border: none;
        border-radius: 25px;
        color: #000000;
        font-family: 'Orbitron', monospace;
        font-weight: 700;
        padding: 0.75rem 2rem;
        margin: 1rem 0;
        width: 100%;
        transition: all 0.3s ease;
        box-shadow: 0 0 20px rgba(255, 0, 0, 0.5);
        text-transform: uppercase;
        letter-spacing: 1px;
        font-size: 1.1rem;
    }
    
    .login-button:hover {
        background: linear-gradient(90deg, #ff4444 0%, #ff0000 100%);
        transform: scale(1.05);
        box-shadow: 0 0 30px rgba(255, 0, 0, 0.7);
    }
    
    .logout-button {
        background: linear-gradient(90deg, #ff0000 0%, #cc0000 100%);
        border: none;
        border-radius: 10px;
        color: #000000;
        font-family: 'Orbitron', monospace;
        font-weight: 700;
        padding: 0.5rem 1rem;
        margin: 1rem;
        transition: all 0.3s ease;
        box-shadow: 0 0 10px rgba(255, 0, 0, 0.5);
        text-transform: uppercase;
        letter-spacing: 1px;
        font-size: 0.8rem;
        position: fixed;
        top: 10px;
        right: 10px;
        z-index: 1000;
    }
    
    /* Custom metric styling */
    [data-testid="stMetricValue"] {
        font-family: 'Orbitron', monospace;
        font-weight: 700;
        color: #ff4444;
    }
    
    [data-testid="stMetricLabel"] {
        font-family: 'Rajdhani', sans-serif;
        font-weight: 600;
        color: #ff8888;
    }
    
    [data-testid="stMetricDelta"] {
        font-family: 'Orbitron', monospace;
    }
    
    .dragon-emoji {
        font-size: 2rem;
        text-shadow: 0 0 10px #ff0000;
    }
</style>
""", unsafe_allow_html=True)

# Simple authentication system
def check_credentials(username, password):
    """Check if username and password are correct"""
    valid_users = {
        "godziller": "dragonfire2025",
        "admin": "cryptoking",
        "trader": "bullmarket"
    }
    return username in valid_users and valid_users[username] == password

def login_page():
    """Display login page"""
    st.markdown("""
    <style>
    .main .block-container {
        padding-top: 0 !important;
        padding-bottom: 0 !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("""
        <div style='
            background: rgba(20, 0, 0, 0.95);
            border: 2px solid rgba(255, 0, 0, 0.6);
            border-radius: 20px;
            padding: 3rem;
            box-shadow: 0 0 50px rgba(255, 0, 0, 0.5);
            text-align: center;
            margin: 2rem 0;
        '>
            <h1 style='
                background: linear-gradient(90deg, #ff0000 0%, #ff4444 100%);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                font-family: Orbitron, monospace;
                font-weight: 900;
                font-size: 2.5rem;
                margin-bottom: 1rem;
                text-shadow: 0 0 20px rgba(255, 0, 0, 0.7);
            '>🐲 GODZILLERS</h1>
            <p style='
                color: #ff6666;
                font-family: Orbitron, monospace;
                font-size: 1rem;
                margin-bottom: 2rem;
                letter-spacing: 2px;
            '>PRIVATE CRYPTO WARFARE SYSTEM</p>
        </div>
        """, unsafe_allow_html=True)
        
        with st.form("login_form"):
            username = st.text_input("👤 DRAGON NAME", placeholder="Enter your dragon name...")
            password = st.text_input("🔐 FIRE BREATH", type="password", placeholder="Enter your fire breath...")
            
            login_button = st.form_submit_button("🔥 IGNITE DRAGON FIRE", use_container_width=True)
            
            if login_button:
                if check_credentials(username, password):
                    st.session_state.logged_in = True
                    st.session_state.username = username
                    st.success("✅ Dragon fire ignited! Access granted.")
                    st.rerun()
                else:
                    st.error("❌ Invalid dragon name or fire breath!")

def get_crypto_prices():
    """Get crypto prices from multiple sources with fallback"""
    coins = {
        'BTCUSDT': 'bitcoin',
        'ETHUSDT': 'ethereum', 
        'ADAUSDT': 'cardano'
    }
    
    prices = {}
    
    try:
        # Try Binance first for all coins
        for symbol in coins.keys():
            try:
                response = requests.get(f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}", timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    prices[symbol] = float(data['price'])
                else:
                    prices[symbol] = None
            except Exception as e:
                prices[symbol] = None
        
        # Fill missing prices with CoinGecko
        missing_coins = [coin_id for symbol, coin_id in coins.items() if prices.get(symbol) is None]
        if missing_coins:
            try:
                coin_ids = ','.join(missing_coins)
                response = requests.get(f"https://api.coingecko.com/api/v3/simple/price?ids={coin_ids}&vs_currencies=usd", timeout=5)
                if response.status_code == 200:
                    gecko_data = response.json()
                    for symbol, coin_id in coins.items():
                        if prices.get(symbol) is None and coin_id in gecko_data:
                            prices[symbol] = float(gecko_data[coin_id]['usd'])
            except Exception as e:
                # If CoinGecko fails, set default prices
                for symbol in coins:
                    if prices.get(symbol) is None:
                        prices[symbol] = 0.0
                
    except Exception as e:
        st.error(f"Error fetching prices: {str(e)}")
        # Set default prices if everything fails
        for symbol in coins:
            prices[symbol] = 0.0
    
    return prices

class BitcoinNodeAnalyzer:
    def __init__(self, data_file="network_data.json"):
        self.data_file = data_file
        self.bitnodes_api ="https://bitnodes.io/api/v1/snapshots/latest/"
        self.load_historical_data()
    
    def load_historical_data(self):
        """Load historical node data from JSON file"""
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r') as f:
                    self.historical_data = json.load(f)
            else:
                self.historical_data = []
        except:
            self.historical_data = []
    
    def save_historical_data(self):
        """Save current data to JSON file"""
        try:
            with open(self.data_file, 'w') as f:
                json.dump(self.historical_data, f, indent=2)
        except Exception as e:
            st.error(f"Error saving data: {e}")
    
    def fetch_node_data(self):
        """Fetch current node data from Bitnodes API"""
        try:
            response = requests.get(self.bitnodes_api, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            total_nodes = data['total_nodes']
            
            # Count active nodes (nodes that responded)
            active_nodes = 0
            tor_nodes = 0
            
            for node_address, node_info in data['nodes'].items():
                # Check if node is active (has response data)
                if node_info and isinstance(node_info, list) and len(node_info) > 0:
                    active_nodes += 1
                
                # Count Tor nodes
                if '.onion' in str(node_address) or '.onion' in str(node_info):
                    tor_nodes += 1
            
            tor_percentage = (tor_nodes / total_nodes) * 100 if total_nodes > 0 else 0
            active_ratio = active_nodes / total_nodes if total_nodes > 0 else 0
            
            return {
                'timestamp': datetime.now().isoformat(),
                'total_nodes': total_nodes,
                'active_nodes': active_nodes,
                'tor_nodes': tor_nodes,
                'tor_percentage': tor_percentage,
                'active_ratio': active_ratio
            }
        except Exception as e:
            st.error(f"Error fetching node data: {e}")
            return None
    
    def get_previous_total_nodes(self):
        """Get previous day's total nodes"""
        if len(self.historical_data) < 2:
            return None
        
        # Get yesterday's data (look for data from ~24 hours ago)
        current_time = datetime.now()
        target_time = current_time - timedelta(hours=24)
        
        # Find the closest snapshot to 24 hours ago
        closest_snapshot = None
        min_time_diff = float('inf')
        
        for snapshot in self.historical_data[:-1]:  # Exclude current
            try:
                snapshot_time = datetime.fromisoformat(snapshot['timestamp'])
                time_diff = abs((snapshot_time - target_time).total_seconds())
                
                if time_diff < min_time_diff:
                    min_time_diff = time_diff
                    closest_snapshot = snapshot
            except:
                continue
        
        return closest_snapshot['total_nodes'] if closest_snapshot else None
    
    def get_previous_tor_percentage(self):
        """Get previous day's Tor percentage for trend analysis"""
        if len(self.historical_data) < 2:
            return None
        
        # Get yesterday's data (look for data from ~24 hours ago)
        current_time = datetime.now()
        target_time = current_time - timedelta(hours=24)
        
        # Find the closest snapshot to 24 hours ago
        closest_snapshot = None
        min_time_diff = float('inf')
        
        for snapshot in self.historical_data[:-1]:  # Exclude current
            try:
                snapshot_time = datetime.fromisoformat(snapshot['timestamp'])
                time_diff = abs((snapshot_time - target_time).total_seconds())
                
                if time_diff < min_time_diff:
                    min_time_diff = time_diff
                    closest_snapshot = snapshot
            except:
                continue
        
        return closest_snapshot['tor_percentage'] if closest_snapshot else None
    
    def calculate_network_signal(self, current_data):
        """Calculate trading signal based on network trends"""
        previous_total = self.get_previous_total_nodes()
        
        if previous_total is None or previous_total == 0:
            return {
                'active_nodes': current_data['active_nodes'],
                'total_nodes': current_data['total_nodes'],
                'previous_total': "No previous data",
                'active_ratio': current_data['active_ratio'],
                'trend': 0,
                'signal': 0,
                'suggestion': "INSUFFICIENT_DATA"
            }
        
        active_ratio = current_data['active_ratio']
        trend = (current_data['total_nodes'] - previous_total) / previous_total
        signal = active_ratio * trend
        
        # Determine suggestion
        if signal > 0.01:
            suggestion = "BUY"
        elif signal < -0.01:
            suggestion = "SELL"
        else:
            suggestion = "SIDEWAYS"
        
        return {
            'active_nodes': current_data['active_nodes'],
            'total_nodes': current_data['total_nodes'],
            'previous_total': previous_total,
            'active_ratio': round(active_ratio, 4),
            'trend': round(trend, 4),
            'signal': round(signal, 4),
            'suggestion': suggestion
        }
    
    def calculate_tor_trend(self, current_tor_percentage):
        """Calculate Tor trend and market bias"""
        previous_tor_percentage = self.get_previous_tor_percentage()
        
        if previous_tor_percentage is None or previous_tor_percentage == 0:
            return {
                'previous_tor': "No data",
                'current_tor': current_tor_percentage,
                'tor_trend': 0,
                'bias': "INSUFFICIENT_DATA"
            }
        
        # Calculate Tor Trend using your formula
        tor_trend = (current_tor_percentage - previous_tor_percentage) / previous_tor_percentage
        
        # Determine market bias based on your rules
        if tor_trend > 0.001:  # Small threshold to account for minor fluctuations
            bias = "BEARISH (Sell Bias)"
        elif tor_trend < -0.001:
            bias = "BULLISH (Buy Bias)"
        else:
            bias = "NEUTRAL"
        
        return {
            'previous_tor': round(previous_tor_percentage, 2),
            'current_tor': round(current_tor_percentage, 2),
            'tor_trend': round(tor_trend * 100, 2),  # Convert to percentage
            'bias': bias
        }

    def calculate_tor_signal(self, current_tor_percentage):
        """Calculate GODZILLERS signal based on Tor percentage changes"""
        previous_tor_percentage = self.get_previous_tor_percentage()
        
        if previous_tor_percentage is None or previous_tor_percentage == 0:
            return {
                'current_tor_pct': current_tor_percentage,
                'previous_tor_pct': 0,
                'tor_pct_change': 0,
                'signal': "INSUFFICIENT_DATA",
                'bias': "NEED MORE DATA"
            }
        
        # Calculate percentage change in Tor nodes
        tor_pct_change = current_tor_percentage - previous_tor_percentage
        
        # GODZILLERS TOR PERCENTAGE SIGNAL LOGIC
        if tor_pct_change >= 1.0:  # Tor percentage increased by 1.0% or more
            signal = "🐲 GODZILLA DUMP 🐲"
            bias = "EXTREME BEARISH"
        elif tor_pct_change >= 0.5:  # Tor percentage increased by 0.5-0.99%
            signal = "🔥 STRONG SELL 🔥"
            bias = "VERY BEARISH"
        elif tor_pct_change >= 0.1:  # Tor percentage increased by 0.1-0.49%
            signal = "SELL"
            bias = "BEARISH"
        elif tor_pct_change <= -1.0:  # Tor percentage decreased by 1.0% or more
            signal = "🐲 GODZILLA PUMP 🐲"
            bias = "EXTREME BULLISH"
        elif tor_pct_change <= -0.5:  # Tor percentage decreased by 0.5-0.99%
            signal = "🚀 STRONG BUY 🚀"
            bias = "VERY BULLISH"
        elif tor_pct_change <= -0.1:  # Tor percentage decreased by 0.1-0.49%
            signal = "BUY"
            bias = "BULLISH"
        else:  # Change between -0.1% and +0.1%
            signal = "HOLD"
            bias = "NEUTRAL"
        
        return {
            'current_tor_pct': current_tor_percentage,
            'previous_tor_pct': previous_tor_percentage,
            'tor_pct_change': tor_pct_change,
            'signal': signal,
            'bias': bias
        }
    
    def update_network_data(self):
        """Fetch new data and update historical records"""
        current_data = self.fetch_node_data()
        if not current_data:
            return False
        
        # Add to historical data
        self.historical_data.append(current_data)
        
        # Keep only last 7 days of data
        if len(self.historical_data) > 1008:
            self.historical_data = self.historical_data[-1008:]
        
        self.save_historical_data()
        return True
    
    def plot_tor_trend_chart(self):
        """Plot Tor percentage trend over time"""
        if len(self.historical_data) < 2:
            return None
        
        # Prepare data for plotting
        dates = []
        tor_percentages = []
        
        for entry in self.historical_data[-24:]:  # Last 24 data points
            try:
                date = datetime.fromisoformat(entry['timestamp']).strftime('%H:%M')
                dates.append(date)
                tor_percentages.append(entry['tor_percentage'])
            except:
                continue
        
        if len(dates) < 2:
            return None
        
        # Create GODZILLERS plot
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=dates,
            y=tor_percentages,
            mode='lines+markers',
            name='Tor %',
            line=dict(color='#ff0000', width=4, shape='spline'),
            marker=dict(size=8, color='#ff4444', line=dict(width=2, color='#ffffff')),
            fill='tozeroy',
            fillcolor='rgba(255, 0, 0, 0.1)'
        ))
        
        fig.update_layout(
            title=dict(
                text="🕵️ DRAGON TOR TREND (Last 24 Hours)",
                font=dict(family='Orbitron', size=20, color='#ffffff')
            ),
            xaxis=dict(
                title="Time",
                gridcolor='rgba(255, 0, 0, 0.1)',
                tickfont=dict(family='Rajdhani', color='#ff8888')
            ),
            yaxis=dict(
                title="Tor Percentage (%)",
                gridcolor='rgba(255, 0, 0, 0.1)',
                tickfont=dict(family='Rajdhani', color='#ff8888')
            ),
            plot_bgcolor='rgba(20, 0, 0, 0.5)',
            paper_bgcolor='rgba(0, 0, 0, 0)',
            font=dict(color='#ffffff'),
            height=400,
            showlegend=True
        )
        
        return fig

def get_coin_display_name(symbol):
    """Get display name for crypto symbols"""
    names = {
        'BTCUSDT': 'Bitcoin',
        'ETHUSDT': 'Ethereum',
        'ADAUSDT': 'Cardano'
    }
    return names.get(symbol, symbol)

def get_coin_emoji(symbol):
    """Get emoji for crypto symbols - GODZILLERS theme"""
    emojis = {
        'BTCUSDT': '🐲',
        'ETHUSDT': '🔥',
        'ADAUSDT': '🎯'
    }
    return emojis.get(symbol, '💀')

def main_app():
    # Initialize analyzer
    analyzer = BitcoinNodeAnalyzer()
    
    # Logout button
    if st.button("🚪 LOGOUT", key="logout", use_container_width=False):
        st.session_state.logged_in = False
        st.session_state.username = None
        st.rerun()
    
    # Welcome message
    st.markdown(f'<p style="text-align: right; color: #ff4444; font-family: Orbitron; margin: 0.5rem 1rem;">Welcome, {st.session_state.username}!</p>', unsafe_allow_html=True)
    
    # GODZILLERS Header
    st.markdown('<h1 class="godzillers-header">🔥 GODZILLERS CRYPTO TRACKER</h1>', unsafe_allow_html=True)
    st.markdown('<p class="godzillers-subheader">Godzillers Eye SIGNALS • TOR PERCENTAGE ANALYSIS • RED HOT PRICES</p>', unsafe_allow_html=True)
    
    # LIVE CRYPTO PRICES SECTION
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    st.markdown('<h2 class="section-header">💰 DRAGON FIRE PRICES</h2>', unsafe_allow_html=True)
    
    # Get all crypto prices
    prices = get_crypto_prices()
    
    if prices:
        # Display BTC price prominently
        btc_price = prices.get('BTCUSDT')
        if btc_price and btc_price > 0:
            st.markdown('<div class="price-glow">', unsafe_allow_html=True)
            col1, col2, col3 = st.columns([2, 1, 1])
            
            with col1:
                st.markdown(f'<div style="text-align: center;"><span style="font-family: Orbitron; font-size: 3rem; font-weight: 900; background: linear-gradient(90deg, #ff0000, #ff4444); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">${btc_price:,.2f}</span></div>', unsafe_allow_html=True)
                st.markdown('<p style="text-align: center; color: #ff8888; font-family: Rajdhani;">BITCOIN PRICE (USD)</p>', unsafe_allow_html=True)
            
            with col2:
                st.metric(
                    label="24H STATUS",
                    value="🔥 LIVE",
                    delta="Godzillers"
                )
            
            with col3:
                st.metric(
                    label="DATA SOURCE", 
                    value="BINANCE API",
                    delta="RED HOT"
                )
            
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.error("❌ Could not fetch Bitcoin price")
        
        # Display all coins in a grid
        st.markdown('<h3 style="font-family: Orbitron; color: #ff4444; margin: 1rem 0;">📊 ALTCOIN BATTLEFIELD</h3>', unsafe_allow_html=True)
        
        # Create columns for coin grid
        coins_to_display = {k: v for k, v in prices.items() if k != 'BTCUSDT' and v and v > 0}
        if coins_to_display:
            # Use 2 columns for cleaner layout with fewer coins
            cols = st.columns(2)
            
            for idx, (symbol, price) in enumerate(coins_to_display.items()):
                if price:
                    with cols[idx % 2]:
                        emoji = get_coin_emoji(symbol)
                        name = get_coin_display_name(symbol)            
                        st.markdown(f'''
                        <div class="coin-card">
                            <div style="text-align: center;">
                                <h4 style="font-family: Orbitron; color: #ff4444; margin: 0.5rem 0; font-size: 1.1rem;">{emoji} {name}</h4>
                                <p style="font-family: Orbitron; font-size: 1.3rem; font-weight: 700; color: #ffffff; margin: 0.5rem 0;">${price:,.2f}</p>
                                <p style="color: #ff8888; font-family: Rajdhani; font-size: 0.9rem; margin: 0;">{symbol}</p>
                            </div>
                        </div>
                        ''', unsafe_allow_html=True)
        else:
            st.warning("⚠️ Could not fetch altcoin prices")
        
        st.markdown(f'<p style="text-align: center; color: #ff8888; font-family: Rajdhani;">🕒 Prices updated: {datetime.now().strftime("%H:%M:%S")}</p>', unsafe_allow_html=True)
    else:
        st.error("❌ Could not fetch crypto prices")
    
    # Refresh button for node data
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown('<h2 class="section-header">📊 GODZILLERS EYE ANALYSIS</h2>', unsafe_allow_html=True)
    with col2:
        if st.button("🐉 UPDATE NODE DATA", key="refresh_main", use_container_width=True, type="primary"):
            with st.spinner("🔥 Scanning network with dragon fire..."):
                if analyzer.update_network_data():
                    st.success("✅ Node data updated successfully!")
                    st.rerun()
                else:
                    st.error("❌ Node data update failed")
    
    # GODZILLERS SIGNAL SECTION
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    st.markdown('<h2 class="section-header">🎯 GODZILLERS EYE SIGNALS</h2>', unsafe_allow_html=True)
    
    # Main content in two columns for better mobile layout
    col1, col2 = st.columns([1, 1])
    
    with col1:
        # Get current node data
        if len(analyzer.historical_data) > 0:
            current_data = analyzer.historical_data[-1]
            
            # TOR TREND ANALYZER SECTION
            st.markdown('<div class="godzillers-card">', unsafe_allow_html=True)
            st.markdown('<h3 style="font-family: Orbitron; color: #ff4444; text-align: center;">🕵️ TOR TREND ANALYZER</h3>', unsafe_allow_html=True)
            
            # Calculate Tor trend
            tor_trend_data = analyzer.calculate_tor_trend(current_data['tor_percentage'])
            
            # Display Tor trend results in a grid
            col1a, col2a, col3a = st.columns(3)
            
            with col1a:
                st.metric("📊 PREVIOUS TOR %", f"{tor_trend_data['previous_tor']}%")
            
            with col2a:
                st.metric("🎯 CURRENT TOR %", f"{tor_trend_data['current_tor']}%")
            
            with col3a:
                trend_value = tor_trend_data['tor_trend']
                st.metric("📈 TOR TREND", f"{trend_value:+.2f}%")
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            # GODZILLERS TOR SIGNAL
            tor_signal_data = analyzer.calculate_tor_signal(current_data['tor_percentage'])
            
            # Display Tor signal comparison
            st.markdown('<div class="godzillers-card">', unsafe_allow_html=True)
            st.markdown('<h3 style="font-family: Orbitron; color: #ff4444; text-align: center;">🐲 GODZILLERS TOR SIGNAL</h3>', unsafe_allow_html=True)
            
            col1b, col2b = st.columns(2)
            
            with col1b:
                st.metric("🕒 PREVIOUS TOR %", f"{tor_signal_data['previous_tor_pct']:.2f}%")
                st.metric("🔥 CURRENT TOR %", f"{tor_signal_data['current_tor_pct']:.2f}%")
            
            with col2b:
                st.metric("📈 TOR % CHANGE", f"{tor_signal_data['tor_pct_change']:+.2f}%")
                st.metric("🎯 GODZILLERS BIAS", tor_signal_data['bias'])
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Display GODZILLERS signal with styling
            if "GODZILLA DUMP" in tor_signal_data['signal']:
                signal_class = "signal-sell"
                emoji = "🐲💀🔥"
                explanation = "GODZILLA DUMP - Tor percentage exploding upward (Extreme Bearish)"
            elif "STRONG SELL" in tor_signal_data['signal']:
                signal_class = "signal-sell"
                emoji = "🐲🔥"
                explanation = "Strong Sell - Tor percentage raging upward (Very Bearish)"
            elif "SELL" in tor_signal_data['signal']:
                signal_class = "signal-sell"
                emoji = "🔴"
                explanation = "Sell - Tor percentage increasing (Bearish)"
            elif "GODZILLA PUMP" in tor_signal_data['signal']:
                signal_class = "signal-buy"
                emoji = "🐲🚀🌟"
                explanation = "GODZILLA PUMP - Tor percentage collapsing (Extreme Bullish)"
            elif "STRONG BUY" in tor_signal_data['signal']:
                signal_class = "signal-buy"
                emoji = "🐲🚀"
                explanation = "Strong Buy - Tor percentage retreating (Very Bullish)"
            elif "BUY" in tor_signal_data['signal']:
                signal_class = "signal-buy"
                emoji = "🟢"
                explanation = "Buy - Tor percentage decreasing (Bullish)"
            else:
                signal_class = "signal-neutral"
                emoji = "🐲⚡"
                explanation = "Battlefield calm - Tor percentage stable (Neutral)"
            
            st.markdown(f'<div class="{signal_class}">', unsafe_allow_html=True)
            st.markdown(f'<h2 style="font-family: Orbitron; text-align: center; margin: 0.5rem 0;">{emoji} {tor_signal_data["signal"]} {emoji}</h2>', unsafe_allow_html=True)
            st.markdown(f'<p style="text-align: center; color: #ff8888; font-family: Rajdhani; margin: 0.5rem 0;">{explanation}</p>', unsafe_allow_html=True)
            st.markdown(f'<p style="text-align: center; font-family: Orbitron; color: #ffffff; margin: 0.5rem 0;">Tor % Change: {tor_signal_data["tor_pct_change"]:+.2f}%</p>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        if len(analyzer.historical_data) > 0:
            current_data = analyzer.historical_data[-1]
            
            # NETWORK TREND SIGNAL SECTION
            st.markdown('<div class="godzillers-card">', unsafe_allow_html=True)
            st.markdown('<h3 style="font-family: Orbitron; color: #ff4444; text-align: center;">📈 NETWORK TREND SIGNAL</h3>', unsafe_allow_html=True)
            
            signal_data = analyzer.calculate_network_signal(current_data)
            
            # Display network metrics
            col1b, col2b = st.columns(2)
            
            with col1b:
                st.metric("🟢 ACTIVE NODES", f"{signal_data['active_nodes']:,}")
                st.metric("📊 TOTAL NODES", f"{signal_data['total_nodes']:,}")
                st.metric("🕒 PREVIOUS TOTAL", f"{signal_data['previous_total']:,}")
            
            with col2b:
                st.metric("⚡ ACTIVE RATIO", f"{signal_data['active_ratio']:.4f}")
                st.metric("📈 TREND", f"{signal_data['trend']:+.4f}")
                st.metric("🎯 FINAL SIGNAL", f"{signal_data['signal']:+.4f}")
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Display signal with GODZILLERS styling
            if signal_data['suggestion'] == "BUY":
                signal_class = "signal-buy"
                emoji = "🐲🚀"
                signal_text = "DRAGON BUY"
            elif signal_data['suggestion'] == "SELL":
                signal_class = "signal-sell"
                emoji = "🐲💀"
                signal_text = "DRAGON SELL"
            else:
                signal_class = "signal-neutral"
                emoji = "🐲⚡"
                signal_text = "DRAGON HOLD"
            
            st.markdown(f'<div class="{signal_class}">', unsafe_allow_html=True)
            st.markdown(f'<h3 style="font-family: Orbitron; text-align: center; margin: 0;">{emoji} {signal_text} SIGNAL {emoji}</h3>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
            
            # MULTI-COIN SIGNALS
            st.markdown('<div class="godzillers-card">', unsafe_allow_html=True)
            st.markdown('<h3 style="font-family: Orbitron; color: #ff4444; text-align: center;">🎯 DRAGON ARMY SIGNALS</h3>', unsafe_allow_html=True)
            
            if prices:
                coins_list = ['BTCUSDT', 'ETHUSDT', 'ADAUSDT']
                
                for symbol in coins_list:
                    if prices.get(symbol):
                        emoji = get_coin_emoji(symbol)
                        name = get_coin_display_name(symbol)
                        price = prices[symbol]
                        
                        # Apply the same Tor percentage signal to all coins
                        if "SELL" in tor_signal_data['signal']:
                            signal_class = "signal-sell"
                            signal_text = tor_signal_data['signal']
                            signal_emoji = "🔴"
                        elif "BUY" in tor_signal_data['signal']:
                            signal_class = "signal-buy"
                            signal_text = tor_signal_data['signal']
                            signal_emoji = "🟢"
                        else:
                            signal_class = "signal-neutral"
                            signal_text = tor_signal_data['signal']
                            signal_emoji = "🟡"
                        
                        st.markdown(f'''
                        <div class="{signal_class}" style="padding: 1rem; margin: 0.5rem 0;">
                            <div style="text-align: center;">
                                <h4 style="font-family: Orbitron; margin: 0.5rem 0; font-size: 1.1rem;">{emoji} {name}</h4>
                                <p style="font-family: Orbitron; font-size: 1.2rem; font-weight: 700; margin: 0.5rem 0;">${price:,.2f}</p>
                                <p style="font-family: Orbitron; font-size: 1rem; margin: 0.5rem 0;">{signal_emoji} {signal_text}</p>
                                <p style="color: #ff8888; font-family: Rajdhani; font-size: 0.8rem; margin: 0;">Δ Tor %: {tor_signal_data['tor_pct_change']:+.2f}%</p>
                            </div>
                        </div>
                        ''', unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
    
    # GODZILLERS Trademark Footer
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="trademark">
    <p>🔥 GODZILLERS CRYPTO WARFARE SYSTEM 🔥</p>
    <p>© 2025 GODZILLERS CRYPTO TRACKER • TOR PERCENTAGE SIGNAL TECHNOLOGY</p>
    <p style="font-size: 0.7rem; color: #ff6666;">FORGE YOUR FORTUNE WITH DRAGON FIRE PRECISION</p>
    </div>
    """, unsafe_allow_html=True)

def main():
    """Main function with login check"""
    # Initialize session state
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'username' not in st.session_state:
        st.session_state.username = None
    
    # Check if user is logged in
    if not st.session_state.logged_in:
        login_page()
    else:
        main_app()

if __name__ == "__main__":
    main()