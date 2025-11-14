import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import time
import json

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
        """Fetch the latest snapshots from Bitnodes API with enhanced error handling"""
        try:
            st.sidebar.info("🔍 Fetching snapshot list...")
            
            # Get snapshot list (sorted by timestamp, latest first)
            snapshots_url = f"{self.base_url}/snapshots/?limit=10"
            response = requests.get(snapshots_url, timeout=15)
            response.raise_for_status()
            snapshots_data = response.json()
            
            if not snapshots_data.get('results'):
                return None, "No snapshot data available"
            
            st.sidebar.info(f"📊 Found {len(snapshots_data['results'])} snapshots")
            
            # Get the two most recent snapshots
            latest_snapshot_url = snapshots_data['results'][0]['url']
            previous_snapshot_url = snapshots_data['results'][1]['url']
            
            st.sidebar.info("📥 Fetching latest snapshot...")
            latest_response = requests.get(latest_snapshot_url, timeout=15)
            latest_response.raise_for_status()
            latest_data = latest_response.json()
            
            st.sidebar.info("📥 Fetching previous snapshot...")
            previous_response = requests.get(previous_snapshot_url, timeout=15)
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
        """Calculate Tor percentage from nodes data with detailed debugging"""
        try:
            if not nodes_data:
                st.sidebar.warning("❌ No nodes data available")
                return 0
            
            total_nodes = len(nodes_data)
            st.sidebar.info(f"📈 Total nodes: {total_nodes}")
            
            if total_nodes == 0:
                st.sidebar.warning("❌ Zero nodes in data")
                return 0
            
            # Count Tor nodes and debug
            tor_nodes = 0
            sample_nodes = []
            
            for i, node in enumerate(nodes_data[:10]):  # Check first 10 nodes
                node_address = node[0] if isinstance(node, list) and len(node) > 0 else str(node)
                sample_nodes.append(node_address)
                if '.onion' in node_address:
                    tor_nodes += 1
                    st.sidebar.info(f"🔍 Found Tor node: {node_address}")
            
            # If no Tor nodes found in sample, check more thoroughly
            if tor_nodes == 0:
                st.sidebar.info("🔍 No Tor nodes in first 10 samples, checking all nodes...")
                tor_nodes = sum(1 for node in nodes_data if '.onion' in (node[0] if isinstance(node, list) and len(node) > 0 else str(node)))
            
            st.sidebar.info(f"🎭 Tor nodes found: {tor_nodes}")
            
            tor_percentage = (tor_nodes / total_nodes) * 100
            st.sidebar.info(f"📊 Tor percentage: {tor_percentage:.2f}%")
            
            return round(tor_percentage, 2)
            
        except Exception as e:
            st.sidebar.error(f"❌ Error calculating Tor %: {str(e)}")
            return 0
    
    def calculate_network_signal(self, current_data, previous_data):
        """Calculate network signal based on the formula"""
        try:
            # Active nodes = nodes that responded and are online
            active_nodes = current_data.get('total_nodes', 0)
            
            current_total_nodes = current_data.get('total_nodes', 0)
            previous_total_nodes = previous_data.get('total_nodes', 0)
            
            st.sidebar.info(f"📡 Current nodes: {current_total_nodes}, Previous: {previous_total_nodes}")
            
            if previous_total_nodes == 0:
                st.sidebar.warning("⚠️ Previous total nodes is zero")
                return 0
            
            # Signal = (Active Nodes ÷ Total Nodes) × ((Current Total Nodes − Previous Total Nodes) ÷ Previous Total Nodes)
            active_ratio = active_nodes / current_total_nodes if current_total_nodes > 0 else 0
            growth_ratio = (current_total_nodes - previous_total_nodes) / previous_total_nodes
            
            signal = active_ratio * growth_ratio
            
            st.sidebar.info(f"📶 Network signal: {signal:.4f}")
            
            return round(signal, 4)
        except Exception as e:
            st.sidebar.error(f"❌ Error calculating signal: {str(e)}")
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
        """Main analysis function with comprehensive debugging"""
        st.sidebar.info("🚀 Starting network analysis...")
        
        snapshots, error = self.fetch_snapshots()
        if error:
            st.sidebar.error(f"❌ {error}")
            return None, error
        
        latest_data = snapshots['latest']
        previous_data = snapshots['previous']
        
        # Debug: Show data structure
        st.sidebar.info("🔍 Latest data keys: " + str(list(latest_data.keys())))
        if 'nodes' in latest_data:
            st.sidebar.info(f"🔍 Latest nodes sample: {len(latest_data['nodes'])} nodes")
            if len(latest_data['nodes']) > 0:
                st.sidebar.info(f"🔍 First node: {str(latest_data['nodes'][0])[:100]}...")
        
        # Calculate Tor percentages
        st.sidebar.info("🧮 Calculating current Tor percentage...")
        current_tor_pct = self.calculate_tor_percentage(latest_data.get('nodes', []))
        
        st.sidebar.info("🧮 Calculating previous Tor percentage...")
        previous_tor_pct = self.calculate_tor_percentage(previous_data.get('nodes', []))
        
        # Calculate Tor trend
        tor_trend = 0
        if previous_tor_pct > 0:
            tor_trend = ((current_tor_pct - previous_tor_pct) / previous_tor_pct) * 100
        
        # Calculate network signal
        st.sidebar.info("📡 Calculating network signal...")
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
        
        st.sidebar.success("✅ Analysis complete!")
        return results, None

# Initialize analyzer
analyzer = BitnodesAnalyzer()

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
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
        padding: 1rem;
        border-left: 4px solid #F7931A;
        margin-bottom: 1rem;
    }
    .trend-up {
        color: #00D4AA;
        font-weight: bold;
    }
    .trend-down {
        color: #FF4B4B;
        font-weight: bold;
    }
    .signal-buy {
        color: #00D4AA;
        font-weight: bold;
        background: rgba(0, 212, 170, 0.1);
        padding: 5px 10px;
        border-radius: 5px;
    }
    .signal-sell {
        color: #FF4B4B;
        font-weight: bold;
        background: rgba(255, 75, 75, 0.1);
        padding: 5px 10px;
        border-radius: 5px;
    }
    .bias-bearish {
        color: #FF4B4B;
        font-weight: bold;
        background: rgba(255, 75, 75, 0.1);
        padding: 5px 10px;
        border-radius: 5px;
    }
    .bias-bullish {
        color: #00D4AA;
        font-weight: bold;
        background: rgba(0, 212, 170, 0.1);
        padding: 5px 10px;
        border-radius: 5px;
    }
    .bias-neutral {
        color: #FFA500;
        font-weight: bold;
        background: rgba(255, 165, 0, 0.1);
        padding: 5px 10px;
        border-radius: 5px;
    }
    @media (max-width: 768px) {
        .main-header {
            font-size: 2rem;
        }
        .metric-card {
            padding: 0.5rem;
        }
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<div class="main-header">₿ Bitcoin Network Analysis</div>', unsafe_allow_html=True)
st.markdown("### Real-time Tor Node Tracking & Network Signals")

# Sidebar
with st.sidebar:
    st.image("https://bitcoin.org/img/icons/opengraph.png", width=80)
    st.title("Settings")
    
    if st.button("🔄 Refresh Data", use_container_width=True, type="primary"):
        st.rerun()
    
    st.markdown("---")
    st.markdown("### Debug Info")
    debug_mode = st.checkbox("Show Debug Information", value=True)
    
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

# Main content
try:
    # Fetch data with progress indicator
    with st.spinner('Fetching data from Bitnodes API...'):
        results, error = analyzer.analyze_network()
    
    if error:
        st.error(f"❌ Error fetching data: {error}")
        
        # Show fallback data for testing
        st.warning("🔄 Showing fallback data for demonstration...")
        results = {
            'current_tor_percentage': 2.5,
            'previous_tor_percentage': 2.3,
            'tor_trend': 8.7,
            'active_nodes': 15500,
            'total_nodes': 15500,
            'previous_total_nodes': 15400,
            'network_signal': 0.0032,
            'tor_bias': "BEARISH (Sell Bias)",
            'signal_bias': "BUY",
            'latest_timestamp': int(time.time()),
            'previous_timestamp': int(time.time()) - 3600,
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        st.info("📊 Using demonstration data. Real data will show when API is accessible.")
    
    # Display metrics in columns
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric(
            label="Current Tor %",
            value=f"{results['current_tor_percentage']}%",
            delta=f"{results['tor_trend']:.2f}%"
        )
        
        # Tor bias with colored badge
        bias_class = "bias-bearish" if "BEARISH" in results['tor_bias'] else "bias-bullish" if "BULLISH" in results['tor_bias'] else "bias-neutral"
        st.markdown(f"Tor Bias: <span class='{bias_class}'>{results['tor_bias']}</span>", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Node information
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric(
            label="Active Nodes",
            value=f"{results['active_nodes']:,}"
        )
        st.metric(
            label="Total Nodes",
            value=f"{results['total_nodes']:,}"
        )
        st.metric(
            label="Previous Total Nodes", 
            value=f"{results['previous_total_nodes']:,}"
        )
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric(
            label="Network Signal",
            value=f"{results['network_signal']:.4f}",
            delta=None
        )
        
        # Signal bias with colored badge
        signal_class = "signal-buy" if results['signal_bias'] == "BUY" else "signal-sell" if results['signal_bias'] == "SELL" else "bias-neutral"
        st.markdown(f"Signal Bias: <span class='{signal_class}'>{results['signal_bias']}</span>", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Previous Tor percentage
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric(
            label="Previous Tor %",
            value=f"{results['previous_tor_percentage']}%"
        )
        st.markdown('</div>', unsafe_allow_html=True)

    # Debug information
    if debug_mode:
        st.markdown("---")
        st.subheader("🔍 Debug Information")
        
        debug_col1, debug_col2 = st.columns(2)
        
        with debug_col1:
            st.write("**Current Analysis:**")
            st.json({
                "current_tor_percentage": results['current_tor_percentage'],
                "previous_tor_percentage": results['previous_tor_percentage'], 
                "tor_trend": results['tor_trend'],
                "network_signal": results['network_signal']
            })
        
        with debug_col2:
            st.write("**Node Statistics:**")
            st.json({
                "active_nodes": results['active_nodes'],
                "total_nodes": results['total_nodes'],
                "previous_total_nodes": results['previous_total_nodes']
            })

    # Visualizations for mobile
    st.markdown("---")
    st.subheader("📊 Network Visualizations")
    
    # Simple bar chart for Tor percentages
    fig_tor = go.Figure(data=[
        go.Bar(name='Current Tor %', x=['Tor %'], y=[results['current_tor_percentage']], marker_color='#F7931A'),
        go.Bar(name='Previous Tor %', x=['Previous Tor %'], y=[results['previous_tor_percentage']], marker_color='#8B4513')
    ])
    fig_tor.update_layout(
        title="Tor Percentage Comparison",
        showlegend=True,
        height=300
    )
    st.plotly_chart(fig_tor, use_container_width=True)
    
    # Network signal indicator
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        signal_value = results['network_signal']
        if signal_value > 0.001:
            st.markdown('<div style="text-align: center; padding: 20px; background: rgba(0, 212, 170, 0.2); border-radius: 10px;">', unsafe_allow_html=True)
            st.markdown("### 🟢 BUY SIGNAL")
            st.markdown(f"**Network Signal: {signal_value:.4f}**")
            st.markdown('</div>', unsafe_allow_html=True)
        elif signal_value < -0.001:
            st.markdown('<div style="text-align: center; padding: 20px; background: rgba(255, 75, 75, 0.2); border-radius: 10px;">', unsafe_allow_html=True)
            st.markdown("### 🔴 SELL SIGNAL")
            st.markdown(f"**Network Signal: {signal_value:.4f}**")
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div style="text-align: center; padding: 20px; background: rgba(255, 165, 0, 0.2); border-radius: 10px;">', unsafe_allow_html=True)
            st.markdown("### 🟡 SIDEWAYS")
            st.markdown(f"**Network Signal: {signal_value:.4f}**")
            st.markdown('</div>', unsafe_allow_html=True)

    # Timestamps
    st.markdown("---")
    def format_timestamp(timestamp):
        return datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
    
    st.caption(f"**Latest Snapshot:** {format_timestamp(results['latest_timestamp'])} | **Previous Snapshot:** {format_timestamp(results['previous_timestamp'])}")
    st.caption(f"*Last analyzed: {results['timestamp']}*")

except Exception as e:
    st.error(f"❌ Application error: {str(e)}")
    st.info("📱 If you're on mobile, try:")
    st.info("• Switching between WiFi and mobile data")
    st.info("• Checking if Bitnodes.io is accessible")
    st.info("• The app will show demonstration data if API is unavailable")

# Mobile-friendly tips
st.sidebar.markdown("---")
st.sidebar.markdown("### 📱 Mobile Tips")
st.sidebar.markdown("""
- Rotate to landscape for better view
- Use refresh button if data doesn't load
- Check internet connection
- API might be slow on mobile networks
""")