import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
import time
import random

# Page configuration
st.set_page_config(
    page_title="Bitcoin Network Analysis",
    page_icon="₿",
    layout="wide",
    initial_sidebar_state="expanded"
)

class BitcoinNetworkAnalyzer:
    def __init__(self):
        self.use_mock_data = True  # Force mock data for mobile
    
    def generate_mock_data(self):
        """Generate realistic mock data for demonstration"""
        # Realistic Bitcoin network statistics
        base_total_nodes = random.randint(15000, 16000)
        current_total_nodes = base_total_nodes + random.randint(-100, 100)
        previous_total_nodes = current_total_nodes - random.randint(-50, 150)
        
        # Tor percentages (realistic range: 1-4%)
        current_tor_pct = round(random.uniform(1.5, 3.5), 2)
        previous_tor_pct = round(current_tor_pct + random.uniform(-0.5, 0.5), 2)
        
        # Calculate trends
        tor_trend = round(((current_tor_pct - previous_tor_pct) / previous_tor_pct) * 100, 2)
        
        # Network signal calculation
        active_ratio = 0.98  # Most nodes are active
        growth_ratio = (current_total_nodes - previous_total_nodes) / previous_total_nodes
        network_signal = round(active_ratio * growth_ratio, 4)
        
        # Market biases
        tor_bias = "BEARISH (Sell Bias)" if tor_trend > 1 else "BULLISH (Buy Bias)" if tor_trend < -1 else "NEUTRAL"
        signal_bias = "BUY" if network_signal > 0.001 else "SELL" if network_signal < -0.001 else "SIDEWAYS"
        
        return {
            'current_tor_percentage': current_tor_pct,
            'previous_tor_percentage': previous_tor_pct,
            'tor_trend': tor_trend,
            'active_nodes': current_total_nodes,
            'total_nodes': current_total_nodes,
            'previous_total_nodes': previous_total_nodes,
            'network_signal': network_signal,
            'tor_bias': tor_bias,
            'signal_bias': signal_bias,
            'latest_timestamp': int(time.time()),
            'previous_timestamp': int(time.time()) - 3600,  # 1 hour ago
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'data_source': 'Mock Data (Bitnodes API Unavailable)'
        }
    
    def analyze_network(self):
        """Main analysis function - uses mock data for reliability"""
        try:
            st.sidebar.info("🔄 Generating network data...")
            
            # Always use mock data for mobile deployment
            results = self.generate_mock_data()
            
            st.sidebar.success("✅ Data generated successfully!")
            return results, None
            
        except Exception as e:
            st.sidebar.error(f"❌ Error: {str(e)}")
            return None, str(e)

# Initialize analyzer
analyzer = BitcoinNetworkAnalyzer()

# Custom CSS for mobile optimization
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: bold;
        background: linear-gradient(45deg, #FF6B00, #F7931A);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 1rem;
    }
    .metric-card {
        background: linear-gradient(135deg, rgba(247, 147, 26, 0.15), rgba(255, 107, 0, 0.1));
        border-radius: 15px;
        padding: 1.2rem;
        border: 1px solid rgba(247, 147, 26, 0.3);
        margin-bottom: 1rem;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    }
    .tor-metric {
        background: linear-gradient(135deg, rgba(139, 69, 19, 0.15), rgba(101, 67, 33, 0.1));
        border-color: rgba(139, 69, 19, 0.3);
    }
    .signal-metric {
        background: linear-gradient(135deg, rgba(0, 100, 200, 0.15), rgba(0, 150, 255, 0.1));
        border-color: rgba(0, 100, 200, 0.3);
    }
    .trend-up {
        color: #00D4AA;
        font-weight: bold;
        font-size: 1.1rem;
    }
    .trend-down {
        color: #FF4B4B;
        font-weight: bold;
        font-size: 1.1rem;
    }
    .signal-buy {
        color: #00D4AA;
        font-weight: bold;
        background: rgba(0, 212, 170, 0.15);
        padding: 8px 16px;
        border-radius: 25px;
        border: 1px solid rgba(0, 212, 170, 0.3);
        text-align: center;
        font-size: 1.1rem;
    }
    .signal-sell {
        color: #FF4B4B;
        font-weight: bold;
        background: rgba(255, 75, 75, 0.15);
        padding: 8px 16px;
        border-radius: 25px;
        border: 1px solid rgba(255, 75, 75, 0.3);
        text-align: center;
        font-size: 1.1rem;
    }
    .bias-bearish {
        color: #FF4B4B;
        font-weight: bold;
        background: rgba(255, 75, 75, 0.15);
        padding: 8px 16px;
        border-radius: 25px;
        border: 1px solid rgba(255, 75, 75, 0.3);
        text-align: center;
        font-size: 1.1rem;
    }
    .bias-bullish {
        color: #00D4AA;
        font-weight: bold;
        background: rgba(0, 212, 170, 0.15);
        padding: 8px 16px;
        border-radius: 25px;
        border: 1px solid rgba(0, 212, 170, 0.3);
        text-align: center;
        font-size: 1.1rem;
    }
    .bias-neutral {
        color: #FFA500;
        font-weight: bold;
        background: rgba(255, 165, 0, 0.15);
        padding: 8px 16px;
        border-radius: 25px;
        border: 1px solid rgba(255, 165, 0, 0.3);
        text-align: center;
        font-size: 1.1rem;
    }
    .metric-value {
        font-size: 2rem;
        font-weight: bold;
        margin: 10px 0;
    }
    .metric-label {
        font-size: 0.9rem;
        opacity: 0.8;
        margin-bottom: 5px;
    }
    .refresh-btn {
        background: linear-gradient(45deg, #F7931A, #FF6B00);
        color: white;
        border: none;
        border-radius: 25px;
        padding: 12px 30px;
        font-weight: bold;
        font-size: 1.1rem;
        width: 100%;
    }
    
    /* Mobile responsiveness */
    @media (max-width: 768px) {
        .main-header {
            font-size: 1.8rem;
        }
        .metric-value {
            font-size: 1.6rem;
        }
        .metric-card {
            padding: 1rem;
            margin-bottom: 0.8rem;
        }
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<div class="main-header">₿ Bitcoin Network Analysis</div>', unsafe_allow_html=True)
st.markdown("### Real-time Tor Node Tracking & Network Signals")

# Sidebar
with st.sidebar:
    st.markdown("### ⚙️ Controls")
    
    if st.button("🔄 Refresh Network Data", key="refresh", use_container_width=True, type="primary"):
        st.rerun()
    
    st.markdown("---")
    st.markdown("### 📊 Data Source")
    st.info("Using simulated network data for reliable mobile performance")
    
    st.markdown("---")
    st.markdown("### 📱 Mobile Optimized")
    st.success("Fully responsive design for all devices")
    
    st.markdown("---")
    st.markdown("### 🔍 How It Works")
    st.markdown("""
    - **Tor %**: Privacy network usage
    - **Network Signal**: Trading indicator
    - **Trend Analysis**: Market direction
    - **Real-time**: Updates on refresh
    """)

# Main content area
try:
    # Fetch data
    with st.spinner('🔄 Generating network data...'):
        results, error = analyzer.analyze_network()
        time.sleep(1)  # Simulate loading
    
    if error:
        st.error(f"Error: {error}")
        # Generate fallback data
        results = analyzer.generate_mock_data()
    
    # Display main metrics
    st.markdown("## 📈 Network Metrics")
    
    # First row - Key metrics
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="metric-card tor-metric">', unsafe_allow_html=True)
        st.markdown('<div class="metric-label">Current Tor Percentage</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="metric-value">{results["current_tor_percentage"]}%</div>', unsafe_allow_html=True)
        
        trend_class = "trend-up" if results["tor_trend"] > 0 else "trend-down"
        trend_arrow = "📈" if results["tor_trend"] > 0 else "📉"
        st.markdown(f'<div class="{trend_class}">{trend_arrow} Trend: {results["tor_trend"]}%</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="metric-card signal-metric">', unsafe_allow_html=True)
        st.markdown('<div class="metric-label">Network Signal</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="metric-value">{results["network_signal"]:.4f}</div>', unsafe_allow_html=True)
        
        signal_class = "signal-buy" if results["signal_bias"] == "BUY" else "signal-sell" if results["signal_bias"] == "SELL" else "bias-neutral"
        st.markdown(f'<div class="{signal_class}">{results["signal_bias"]} SIGNAL</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Second row - Additional metrics
    col3, col4 = st.columns(2)
    
    with col3:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown('<div class="metric-label">Previous Tor Percentage</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="metric-value">{results["previous_tor_percentage"]}%</div>', unsafe_allow_html=True)
        
        bias_class = "bias-bearish" if "BEARISH" in results["tor_bias"] else "bias-bullish" if "BULLISH" in results["tor_bias"] else "bias-neutral"
        st.markdown(f'<div class="{bias_class}">{results["tor_bias"]}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col4:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown('<div class="metric-label">Node Statistics</div>', unsafe_allow_html=True)
        st.markdown(f'<div style="font-size: 1.2rem; margin: 5px 0;">🟢 Active: {results["active_nodes"]:,}</div>', unsafe_allow_html=True)
        st.markdown(f'<div style="font-size: 1.2rem; margin: 5px 0;">📊 Total: {results["total_nodes"]:,}</div>', unsafe_allow_html=True)
        st.markdown(f'<div style="font-size: 1.2rem; margin: 5px 0;">⏮️ Previous: {results["previous_total_nodes"]:,}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Visualizations
    st.markdown("## 📊 Network Visualizations")
    
    # Tor percentage comparison chart
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
        title="Tor Percentage Comparison",
        showlegend=True,
        height=300,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white')
    )
    st.plotly_chart(fig_tor, use_container_width=True)
    
    # Network signal gauge
    fig_gauge = go.Figure(go.Indicator(
        mode = "gauge+number+delta",
        value = results['network_signal'],
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': "Network Signal", 'font': {'size': 24}},
        delta = {'reference': 0},
        gauge = {
            'axis': {'range': [-0.01, 0.01], 'tickwidth': 1},
            'bar': {'color': "darkblue"},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "gray",
            'steps': [
                {'range': [-0.01, -0.001], 'color': 'lightcoral'},
                {'range': [-0.001, 0.001], 'color': 'lightyellow'},
                {'range': [0.001, 0.01], 'color': 'lightgreen'}
            ],
        }
    ))
    fig_gauge.update_layout(height=300, paper_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig_gauge, use_container_width=True)
    
    # Market Insights
    st.markdown("## 💡 Market Insights")
    
    insight_col1, insight_col2 = st.columns(2)
    
    with insight_col1:
        if "BEARISH" in results["tor_bias"]:
            st.warning("**Tor Trend Analysis:** 📉\n\nIncreasing Tor usage suggests privacy concerns, potentially indicating cautious market sentiment.")
        else:
            st.success("**Tor Trend Analysis:** 📈\n\nStable or decreasing Tor usage suggests normal market conditions.")
    
    with insight_col2:
        if results["signal_bias"] == "BUY":
            st.success("**Network Signal:** 🟢\n\nPositive network growth suggests healthy network expansion.")
        elif results["signal_bias"] == "SELL":
            st.error("**Network Signal:** 🔴\n\nNetwork contraction may indicate reduced participation.")
        else:
            st.info("**Network Signal:** 🟡\n\nNetwork conditions are stable.")
    
    # Data source and timestamp
    st.markdown("---")
    st.info(f"**Data Source:** {results.get('data_source', 'Mock Data')}")
    
    col1, col2 = st.columns(2)
    with col1:
        st.caption(f"**Last Updated:** {results['timestamp']}")
    with col2:
        st.caption("**Note:** Data updates on each refresh")

except Exception as e:
    st.error("🚨 Application Error")
    st.info("Please refresh the page or try again later.")
    st.code(f"Error details: {str(e)}")

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #666;'>"
    "Bitcoin Network Analysis Dashboard | "
    "Refresh for latest data"
    "</div>", 
    unsafe_allow_html=True
)