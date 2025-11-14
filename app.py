import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
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
    
    def fetch_real_data(self):
        """Fetch real data from Bitnodes API"""
        try:
            # Get the latest snapshots
            snapshots_url = f"{self.base_url}/snapshots/?limit=5"
            response = requests.get(snapshots_url, timeout=30)
            response.raise_for_status()
            snapshots_data = response.json()
            
            if not snapshots_data.get('results'):
                return None, "No snapshot data available"
            
            # Get the two most recent snapshots
            latest_snapshot = snapshots_data['results'][0]
            previous_snapshot = snapshots_data['results'][1]
            
            # Fetch detailed data for latest snapshot
            latest_url = latest_snapshot['url']
            latest_response = requests.get(latest_url, timeout=30)
            latest_response.raise_for_status()
            latest_data = latest_response.json()
            
            # Fetch detailed data for previous snapshot  
            previous_url = previous_snapshot['url']
            previous_response = requests.get(previous_url, timeout=30)
            previous_response.raise_for_status()
            previous_data = previous_response.json()
            
            return {
                'latest': latest_data,
                'previous': previous_data,
                'latest_timestamp': latest_snapshot['timestamp'],
                'previous_timestamp': previous_snapshot['timestamp']
            }, None
            
        except Exception as e:
            return None, f"API Error: {str(e)}"
    
    def calculate_tor_percentage(self, nodes_data):
        """Calculate real Tor percentage from nodes data"""
        try:
            if not nodes_data:
                return 0
                
            total_nodes = len(nodes_data)
            tor_nodes = 0
            
            for node in nodes_data:
                if isinstance(node, list) and len(node) > 0:
                    node_address = node[0]
                    if '.onion' in str(node_address):
                        tor_nodes += 1
            
            tor_percentage = (tor_nodes / total_nodes) * 100
            return round(tor_percentage, 2)
        except Exception:
            return 0
    
    def calculate_network_signal(self, current_data, previous_data):
        """Calculate network signal using the real formula"""
        try:
            # Formula: Signal = (Active Nodes ÷ Total Nodes) × ((Current Total Nodes − Previous Total Nodes) ÷ Previous Total Nodes)
            
            # Active nodes = total_nodes in Bitnodes response (they're all active/online)
            active_nodes = current_data.get('total_nodes', 0)
            current_total_nodes = current_data.get('total_nodes', 0)
            previous_total_nodes = previous_data.get('total_nodes', 0)
            
            if previous_total_nodes == 0:
                return 0
            
            active_ratio = active_nodes / current_total_nodes
            growth_ratio = (current_total_nodes - previous_total_nodes) / previous_total_nodes
            
            signal = active_ratio * growth_ratio
            return round(signal, 6)  # More precision for small values
            
        except Exception:
            return 0
    
    def get_market_bias(self, tor_trend, network_signal):
        """Determine market bias based on real trends"""
        tor_bias = "NEUTRAL"
        if tor_trend > 0:
            tor_bias = "BEARISH (Sell Bias)"
        elif tor_trend < 0:
            tor_bias = "BULLISH (Buy Bias)"
        
        signal_bias = "SIDEWAYS"
        if network_signal > 0:
            signal_bias = "BUY"
        elif network_signal < 0:
            signal_bias = "SELL"
        
        return tor_bias, signal_bias
    
    def analyze_network(self):
        """Main analysis with real data"""
        try:
            # Fetch real data
            snapshots, error = self.fetch_real_data()
            if error:
                return None, error
            
            latest_data = snapshots['latest']
            previous_data = snapshots['previous']
            
            # Calculate real Tor percentages
            current_tor_pct = self.calculate_tor_percentage(latest_data.get('nodes', []))
            previous_tor_pct = self.calculate_tor_percentage(previous_data.get('nodes', []))
            
            # Calculate Tor trend
            tor_trend = 0
            if previous_tor_pct > 0:
                tor_trend = ((current_tor_pct - previous_tor_pct) / previous_tor_pct) * 100
            
            # Calculate real network signal
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
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'data_source': 'Bitnodes.io API'
            }
            
            return results, None
            
        except Exception as e:
            return None, f"Analysis error: {str(e)}"

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
        border-radius: 15px;
        padding: 1.5rem;
        border-left: 4px solid #F7931A;
        margin-bottom: 1rem;
    }
    .tor-card {
        border-left-color: #8B4513;
    }
    .signal-card {
        border-left-color: #0064C8;
    }
    .metric-value {
        font-size: 2.5rem;
        font-weight: bold;
        margin: 10px 0;
    }
    .metric-label {
        font-size: 1rem;
        opacity: 0.8;
        margin-bottom: 5px;
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
        background: rgba(0, 212, 170, 0.2);
        padding: 8px 16px;
        border-radius: 20px;
        display: inline-block;
    }
    .signal-sell {
        color: #FF4B4B;
        font-weight: bold;
        background: rgba(255, 75, 75, 0.2);
        padding: 8px 16px;
        border-radius: 20px;
        display: inline-block;
    }
    .bias-bearish {
        color: #FF4B4B;
        font-weight: bold;
        background: rgba(255, 75, 75, 0.2);
        padding: 8px 16px;
        border-radius: 20px;
        display: inline-block;
    }
    .bias-bullish {
        color: #00D4AA;
        font-weight: bold;
        background: rgba(0, 212, 170, 0.2);
        padding: 8px 16px;
        border-radius: 20px;
        display: inline-block;
    }
    .bias-neutral {
        color: #FFA500;
        font-weight: bold;
        background: rgba(255, 165, 0, 0.2);
        padding: 8px 16px;
        border-radius: 20px;
        display: inline-block;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<div class="main-header">₿ Bitcoin Network Analysis</div>', unsafe_allow_html=True)
st.markdown("### Real-time Tor Node Tracking & Network Signals")

# Sidebar
with st.sidebar:
    st.image("https://bitcoin.org/img/icons/opengraph.png", width=80)
    st.title("Controls")
    
    if st.button("🔄 Refresh Real Data", use_container_width=True, type="primary"):
        st.rerun()
    
    st.markdown("---")
    st.markdown("### Formulas")
    st.markdown("""
    **Tor %** = (Tor Nodes / Total Nodes) × 100
    
    **Signal** = (Active Nodes ÷ Total Nodes) × 
                ((Current Nodes − Previous Nodes) ÷ Previous Nodes)
    
    **Tor Trend** = ((Current Tor % − Previous Tor %) ÷ Previous Tor %) × 100
    """)
    
    st.markdown("---")
    st.markdown("### Data Source")
    st.markdown("[Bitnodes.io API](https://bitnodes.io/)")

# Main content
try:
    # Fetch real data
    with st.spinner('📡 Fetching real data from Bitnodes API...'):
        results, error = analyzer.analyze_network()
    
    if error:
        st.error(f"❌ Error fetching real data: {error}")
        st.info("This might be due to:")
        st.info("• API rate limiting")
        st.info("• Network connectivity issues")
        st.info("• Bitnodes API changes")
        st.info("Please try refreshing in a few moments.")
    else:
        # Display real metrics
        st.success(f"✅ Real data fetched from Bitnodes API")
        
        # Key metrics row
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('<div class="metric-card tor-card">', unsafe_allow_html=True)
            st.markdown('<div class="metric-label">Current Tor Percentage</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="metric-value">{results["current_tor_percentage"]}%</div>', unsafe_allow_html=True)
            
            # Tor trend
            trend_class = "trend-up" if results["tor_trend"] > 0 else "trend-down"
            trend_symbol = "↗️" if results["tor_trend"] > 0 else "↘️"
            st.markdown(f'<div class="{trend_class}">{trend_symbol} Trend: {results["tor_trend"]:.2f}%</div>', unsafe_allow_html=True)
            
            # Tor bias
            bias_class = "bias-bearish" if "BEARISH" in results["tor_bias"] else "bias-bullish" if "BULLISH" in results["tor_bias"] else "bias-neutral"
            st.markdown(f'<div class="{bias_class}" style="margin-top: 10px;">{results["tor_bias"]}</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="metric-card signal-card">', unsafe_allow_html=True)
            st.markdown('<div class="metric-label">Network Signal</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="metric-value">{results["network_signal"]:.6f}</div>', unsafe_allow_html=True)
            
            # Signal bias
            signal_class = "signal-buy" if results["signal_bias"] == "BUY" else "signal-sell" if results["signal_bias"] == "SELL" else "bias-neutral"
            st.markdown(f'<div class="{signal_class}">{results["signal_bias"]} SIGNAL</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Additional metrics row
        col3, col4 = st.columns(2)
        
        with col3:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.markdown('<div class="metric-label">Previous Tor Percentage</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="metric-value">{results["previous_tor_percentage"]}%</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
            
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.markdown('<div class="metric-label">Node Statistics</div>', unsafe_allow_html=True)
            st.markdown(f'**Active Nodes:** {results["active_nodes"]:,}')
            st.markdown(f'**Total Nodes:** {results["total_nodes"]:,}')
            st.markdown(f'**Previous Total Nodes:** {results["previous_total_nodes"]:,}')
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col4:
            # Network signal calculation breakdown
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.markdown('<div class="metric-label">Signal Calculation</div>', unsafe_allow_html=True)
            
            active_ratio = results["active_nodes"] / results["total_nodes"]
            growth_ratio = (results["total_nodes"] - results["previous_total_nodes"]) / results["previous_total_nodes"]
            
            st.markdown(f"""
            ```
            Active Ratio = {active_ratio:.4f}
            Growth Ratio = {growth_ratio:.6f}
            Signal = {active_ratio:.4f} × {growth_ratio:.6f}
            Signal = {results["network_signal"]:.6f}
            ```
            """)
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Visualizations
        st.markdown("## 📊 Real Data Visualizations")
        
        # Tor comparison chart
        fig_tor = go.Figure()
        fig_tor.add_trace(go.Bar(
            name='Current Tor %',
            x=['Tor Nodes'],
            y=[results['current_tor_percentage']],
            marker_color='#F7931A',
            text=[f"{results['current_tor_percentage']}%"],
            textposition='auto',
        ))
        fig_tor.add_trace(go.Bar(
            name='Previous Tor %', 
            x=['Previous'],
            y=[results['previous_tor_percentage']],
            marker_color='#8B4513',
            text=[f"{results['previous_tor_percentage']}%"],
            textposition='auto',
        ))
        fig_tor.update_layout(
            title="Real Tor Percentage Comparison",
            showlegend=True,
            height=400
        )
        st.plotly_chart(fig_tor, use_container_width=True)
        
        # Network nodes trend
        fig_nodes = go.Figure()
        fig_nodes.add_trace(go.Indicator(
            mode = "number+delta",
            value = results['total_nodes'],
            number = {'valueformat': ','},
            delta = {'reference': results['previous_total_nodes'], 'relative': False},
            title = {"text": "Total Nodes Trend"},
            domain = {'row': 0, 'column': 0}
        ))
        fig_nodes.update_layout(
            grid = {'rows': 1, 'columns': 1, 'pattern': "independent"},
            height=200
        )
        st.plotly_chart(fig_nodes, use_container_width=True)
        
        # Raw data preview
        st.markdown("## 🔍 Raw Data Preview")
        
        with st.expander("Show calculation details"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Current Snapshot:**")
                st.json({
                    "total_nodes": results["total_nodes"],
                    "tor_percentage": results["current_tor_percentage"],
                    "timestamp": datetime.fromtimestamp(results["latest_timestamp"]).strftime('%Y-%m-%d %H:%M:%S')
                })
            
            with col2:
                st.markdown("**Previous Snapshot:**")
                st.json({
                    "total_nodes": results["previous_total_nodes"], 
                    "tor_percentage": results["previous_tor_percentage"],
                    "timestamp": datetime.fromtimestamp(results["previous_timestamp"]).strftime('%Y-%m-%d %H:%M:%S')
                })
        
        # Timestamps
        st.markdown("---")
        def format_timestamp(timestamp):
            return datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
        
        st.caption(f"**Latest Snapshot:** {format_timestamp(results['latest_timestamp'])}")
        st.caption(f"**Previous Snapshot:** {format_timestamp(results['previous_timestamp'])}") 
        st.caption(f"*Analysis performed: {results['timestamp']}*")
        st.caption(f"**Data Source:** {results['data_source']}")

except Exception as e:
    st.error(f"❌ Application error: {str(e)}")
    st.info("Please try refreshing the page or check your internet connection.")

# Auto-refresh option
st.sidebar.markdown("---")
if st.sidebar.button("🔄 Auto-refresh in 5s", use_container_width=True):
    time.sleep(5)
    st.rerun()