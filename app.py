import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import time

# Page configuration
st.set_page_config(
    page_title="Bitcoin Network Analysis",
    page_icon="₿",
    layout="wide",
    initial_sidebar_state="expanded"
)

class BitnodesAnalyzer:
    def __init__(self):
        self.base_url = "https://bitnodes.io/api/v1"
    
    def fetch_snapshots(self):
        """Fetch the latest snapshots from Bitnodes API"""
        try:
            # Get snapshot list (sorted by timestamp, latest first)
            snapshots_url = f"{self.base_url}/snapshots/?limit=10"
            response = requests.get(snapshots_url, timeout=10)
            response.raise_for_status()
            snapshots_data = response.json()
            
            if not snapshots_data.get('results'):
                return None, "No snapshot data available"
            
            # Get the two most recent snapshots
            latest_snapshot_url = snapshots_data['results'][0]['url']
            previous_snapshot_url = snapshots_data['results'][1]['url']
            
            # Fetch detailed data for both snapshots
            latest_response = requests.get(latest_snapshot_url, timeout=10)
            latest_response.raise_for_status()
            latest_data = latest_response.json()
            
            previous_response = requests.get(previous_snapshot_url, timeout=10)
            previous_response.raise_for_status()
            previous_data = previous_response.json()
            
            return {
                'latest': latest_data,
                'previous': previous_data,
                'latest_timestamp': snapshots_data['results'][0]['timestamp'],
                'previous_timestamp': snapshots_data['results'][1]['timestamp']
            }, None
            
        except requests.exceptions.RequestException as e:
            return None, f"API request failed: {str(e)}"
        except (KeyError, IndexError) as e:
            return None, f"Data parsing error: {str(e)}"
        except Exception as e:
            return None, f"Unexpected error: {str(e)}"
    
    def calculate_tor_percentage(self, nodes_data):
        """Calculate Tor percentage from nodes data"""
        try:
            total_nodes = len(nodes_data)
            if total_nodes == 0:
                return 0
            
            tor_nodes = sum(1 for node in nodes_data if '.onion' in node[0])
            tor_percentage = (tor_nodes / total_nodes) * 100
            return round(tor_percentage, 2)
        except Exception:
            return 0
    
    def calculate_network_signal(self, current_data, previous_data):
        """Calculate network signal based on the formula"""
        try:
            # Active nodes = nodes that responded and are online
            active_nodes = current_data.get('total_nodes', 0)
            
            current_total_nodes = current_data.get('total_nodes', 0)
            previous_total_nodes = previous_data.get('total_nodes', 0)
            
            if previous_total_nodes == 0:
                return 0
            
            # Signal = (Active Nodes ÷ Total Nodes) × ((Current Total Nodes − Previous Total Nodes) ÷ Previous Total Nodes)
            active_ratio = active_nodes / current_total_nodes if current_total_nodes > 0 else 0
            growth_ratio = (current_total_nodes - previous_total_nodes) / previous_total_nodes
            
            signal = active_ratio * growth_ratio
            return round(signal, 4)
        except Exception:
            return 0
    
    def get_market_bias(self, tor_trend, network_signal):
        """Determine market bias based on trends"""
        tor_bias = "NEUTRAL"
        if tor_trend > 1:  # Using 1% threshold for significant change
            tor_bias = "BEARISH (Sell Bias)"
        elif tor_trend < -1:
            tor_bias = "BULLISH (Buy Bias)"
        
        signal_bias = "SIDEWAYS"
        if network_signal > 0.001:  # Small threshold for signal
            signal_bias = "BUY"
        elif network_signal < -0.001:
            signal_bias = "SELL"
        
        return tor_bias, signal_bias
    
    def analyze_network(self):
        """Main analysis function"""
        snapshots, error = self.fetch_snapshots()
        if error:
            return None, error
        
        latest_data = snapshots['latest']
        previous_data = snapshots['previous']
        
        # Calculate Tor percentages
        current_tor_pct = self.calculate_tor_percentage(latest_data.get('nodes', []))
        previous_tor_pct = self.calculate_tor_percentage(previous_data.get('nodes', []))
        
        # Calculate Tor trend
        tor_trend = 0
        if previous_tor_pct > 0:
            tor_trend = ((current_tor_pct - previous_tor_pct) / previous_tor_pct) * 100
        
        # Calculate network signal
        network_signal = self.calculate_network_signal(latest_data, previous_data)
        
        # Get market biases
        tor_bias, signal_bias = self.get_market_bias(tor_trend, network_signal)
        
        # Prepare results
        results = {
            'current_tor_percentage': current_tor_pct,
            'previous_tor_percentage': previous_tor_pct,
            'tor_trend': round(tor_trend, 2),
            'active_nodes': latest_data.get('total_nodes', 0),
            'total_nodes': latest_data.get('total_nodes', 0),
            'previous_total_nodes': previous_data.get('total_nodes', 0),
            'network_signal': network_signal,
            'tor_bias': tor_bias,
            'signal_bias': signal_bias,
            'latest_timestamp': snapshots['latest_timestamp'],
            'previous_timestamp': snapshots['previous_timestamp'],
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        return results, None

# Initialize analyzer
analyzer = BitnodesAnalyzer()

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        background: linear-gradient(45deg, #FF6B00, #F7931A);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 1rem;
    }
    .metric-card {
        background: rgba(255, 255, 255, 0.1);
        border-radius: 10px;
        padding: 1.5rem;
        border-left: 4px solid #F7931A;
    }
    .trend-up {
        color: #00D4AA;
    }
    .trend-down {
        color: #FF4B4B;
    }
    .signal-buy {
        color: #00D4AA;
        font-weight: bold;
    }
    .signal-sell {
        color: #FF4B4B;
        font-weight: bold;
    }
    .bias-bearish {
        color: #FF4B4B;
        font-weight: bold;
    }
    .bias-bullish {
        color: #00D4AA;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<div class="main-header">₿ Bitcoin Network Analysis</div>', unsafe_allow_html=True)
st.markdown("### Real-time Tor Node Tracking & Network Signals")

# Sidebar
with st.sidebar:
    st.image("https://bitcoin.org/img/icons/opengraph.png", width=100)
    st.title("Settings")
    
    if st.button("🔄 Refresh Data", use_container_width=True):
        st.rerun()
    
    st.markdown("---")
    st.markdown("### About")
    st.markdown("""
    This app analyzes Bitcoin network data from Bitnodes API to provide:
    - **Tor Node Percentage**: Privacy network usage
    - **Network Signal**: Trading insights
    - **Market Bias Indicators**: Based on network trends
    """)
    
    st.markdown("---")
    st.markdown("### Data Source")
    st.markdown("[Bitnodes.io API](https://bitnodes.io/)")
    st.markdown(f"Last update: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# Main content
try:
    # Fetch data with progress indicator
    with st.spinner('Fetching data from Bitnodes API...'):
        results, error = analyzer.analyze_network()
    
    if error:
        st.error(f"Error fetching data: {error}")
        st.stop()
    
    # Display metrics in columns
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric(
            label="Current Tor %",
            value=f"{results['current_tor_percentage']}%",
            delta=f"{results['tor_trend']:.2f}%"
        )
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric(
            label="Network Signal",
            value=f"{results['network_signal']:.4f}",
            delta=None
        )
        bias_color = "signal-buy" if results['signal_bias'] == "BUY" else "signal-sell" if results['signal_bias'] == "SELL" else ""
        st.markdown(f"<span class='{bias_color}'>{results['signal_bias']}</span>", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric(
            label="Active Nodes",
            value=f"{results['active_nodes']:,}"
        )
        st.metric(
            label="Total Nodes",
            value=f"{results['total_nodes']:,}"
        )
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col4:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric(
            label="Previous Tor %",
            value=f"{results['previous_tor_percentage']}%"
        )
        bias_color = "bias-bullish" if "BULLISH" in results['tor_bias'] else "bias-bearish" if "BEARISH" in results['tor_bias'] else ""
        st.markdown(f"<span class='{bias_color}'>{results['tor_bias']}</span>", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # Charts and Visualizations
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Tor Percentage Comparison
        fig_tor = go.Figure()
        fig_tor.add_trace(go.Indicator(
            mode = "number+delta",
            value = results['current_tor_percentage'],
            number = {'suffix': "%", 'font': {'size': 40}},
            delta = {'reference': results['previous_tor_percentage'], 'relative': False, 'font': {'size': 20}},
            title = {"text": "Tor Percentage Trend"},
            domain = {'row': 0, 'column': 0}
        ))
        fig_tor.update_layout(
            height=200,
            margin=dict(l=10, r=10, t=50, b=10)
        )
        st.plotly_chart(fig_tor, use_container_width=True)
        
        # Node Distribution
        tor_nodes = results['current_tor_percentage'] / 100 * results['total_nodes']
        regular_nodes = results['total_nodes'] - tor_nodes
        
        fig_nodes = px.pie(
            values=[regular_nodes, tor_nodes],
            names=['Regular Nodes', 'Tor Nodes'],
            title="Node Distribution",
            color_discrete_sequence=['#F7931A', '#8B4513']
        )
        st.plotly_chart(fig_nodes, use_container_width=True)
    
    with col2:
        # Network Signal Gauge
        fig_signal = go.Figure(go.Indicator(
            mode = "gauge+number+delta",
            value = results['network_signal'],
            domain = {'x': [0, 1], 'y': [0, 1]},
            title = {'text': "Network Signal", 'font': {'size': 24}},
            delta = {'reference': 0},
            gauge = {
                'axis': {'range': [-0.01, 0.01]},
                'bar': {'color': "darkblue"},
                'steps': [
                    {'range': [-0.01, -0.001], 'color': "lightcoral"},
                    {'range': [-0.001, 0.001], 'color': "lightyellow"},
                    {'range': [0.001, 0.01], 'color': "lightgreen"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 0.009
                }
            }
        ))
        fig_signal.update_layout(height=300)
        st.plotly_chart(fig_signal, use_container_width=True)

    # Detailed Data Table
    st.markdown("---")
    st.subheader("Detailed Network Metrics")
    
    metrics_data = {
        "Metric": [
            "Current Tor Percentage",
            "Previous Tor Percentage", 
            "Tor Trend",
            "Network Signal",
            "Active Nodes",
            "Total Nodes",
            "Previous Total Nodes",
            "Tor Bias",
            "Signal Bias"
        ],
        "Value": [
            f"{results['current_tor_percentage']}%",
            f"{results['previous_tor_percentage']}%",
            f"{results['tor_trend']:.2f}%",
            f"{results['network_signal']:.4f}",
            f"{results['active_nodes']:,}",
            f"{results['total_nodes']:,}",
            f"{results['previous_total_nodes']:,}",
            results['tor_bias'],
            results['signal_bias']
        ]
    }
    
    df = pd.DataFrame(metrics_data)
    st.dataframe(df, use_container_width=True, hide_index=True)

    # Interpretation Guide
    st.markdown("---")
    st.subheader("📊 Interpretation Guide")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        ### Tor Trend Analysis
        - **📈 Tor Trend > 0%**: BEARISH (Sell Bias)
          - Increasing privacy usage may indicate cautious market sentiment
        - **📉 Tor Trend < 0%**: BULLISH (Buy Bias)  
          - Decreasing privacy usage may indicate confident market sentiment
        - **➡️ Tor Trend ≈ 0%**: NEUTRAL
          - Stable privacy network usage
        """)
    
    with col2:
        st.markdown("""
        ### Network Signal
        - **🟢 Signal > 0**: BUY
          - Network growth with high active node participation
        - **🔴 Signal < 0**: SELL
          - Network contraction or low participation
        - **🟡 Signal ≈ 0**: SIDEWAYS
          - Stable network conditions
        """)

    # Timestamps
    st.markdown("---")
    col1, col2 = st.columns(2)
    
    def format_timestamp(timestamp):
        return datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
    
    with col1:
        st.markdown(f"**Latest Snapshot:** {format_timestamp(results['latest_timestamp'])}")
    with col2:
        st.markdown(f"**Previous Snapshot:** {format_timestamp(results['previous_timestamp'])}")
    
    st.markdown(f"*Last analyzed: {results['timestamp']}*")

except Exception as e:
    st.error(f"Application error: {str(e)}")
    st.info("Please try refreshing the data or check your internet connection.")

# Auto-refresh option
st.sidebar.markdown("---")
auto_refresh = st.sidebar.checkbox("Auto-refresh every 5 minutes")
if auto_refresh:
    time.sleep(300)
    st.rerun()