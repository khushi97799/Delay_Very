import streamlit as st
import pandas as pd
import networkx as nx
import plotly.graph_objects as go
import plotly.express as px

st.set_page_config(
    page_title="Delhivery Ops Intelligence",
    layout="wide",
    page_icon="📦"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600&family=Syne:wght@600;700;800&family=Inter:wght@400;500;600&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

.stApp { background-color: #0d0f18; color: #e2e8f0; }

[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #111320 0%, #0d0f18 100%);
    border-right: 1px solid #1e293b;
}
[data-testid="stSidebar"] * { color: #cbd5e1 !important; }

[data-testid="metric-container"] {
    background: linear-gradient(135deg, #13172b 60%, #1a1f35);
    border: 1px solid #1e293b;
    border-left: 4px solid #6366f1;
    border-radius: 12px;
    padding: 18px 20px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.4);
}
[data-testid="metric-container"] label {
    color: #7c86a2 !important;
    font-size: 0.7rem !important;
    font-weight: 600 !important;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    font-family: 'JetBrains Mono', monospace !important;
}
[data-testid="metric-container"] [data-testid="metric-value"] {
    color: #f1f5f9 !important;
    font-size: 1.7rem !important;
    font-weight: 700 !important;
    font-family: 'Syne', sans-serif !important;
}

h1 {
    font-family: 'Syne', sans-serif !important;
    color: #f1f5f9 !important;
    font-size: 2rem !important;
    font-weight: 800 !important;
    letter-spacing: -0.02em;
}
h2, h3 {
    font-family: 'Syne', sans-serif !important;
    color: #a5b4fc !important;
    font-weight: 700 !important;
}

hr {
    border: none !important;
    border-top: 1px solid #1e293b !important;
    margin: 1.8rem 0 !important;
}

[data-testid="stDataFrame"] {
    border: 1px solid #1e293b !important;
    border-radius: 10px;
    overflow: hidden;
}

.stCaption {
    color: #475569 !important;
    font-size: 0.73rem;
    text-align: center;
    font-family: 'JetBrains Mono', monospace;
    letter-spacing: 0.05em;
}

.badge {
    display: inline-block;
    background: #1e293b;
    color: #a5b4fc;
    font-size: 0.68rem;
    font-family: 'JetBrains Mono', monospace;
    padding: 3px 10px;
    border-radius: 20px;
    border: 1px solid #312e81;
    margin-right: 6px;
    letter-spacing: 0.06em;
}

.section-desc {
    color: #64748b;
    font-size: 0.82rem;
    margin-top: -10px;
    margin-bottom: 14px;
    font-style: italic;
}

.hero-tag {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.7rem;
    color: #6366f1;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    margin-bottom: 4px;
}
</style>
""", unsafe_allow_html=True)

# ── THEME DICTS ──
DARK_LAYOUT = dict(
    plot_bgcolor='#13172b',
    paper_bgcolor='#13172b',
    font=dict(family='Inter', size=11, color='#cbd5e1'),
    title_font=dict(size=13, color='#e2e8f0', family='Syne'),
)

DARK_LEGEND = dict(bgcolor='#0d0f18', bordercolor='#1e293b', borderwidth=1)

DARK_AXIS = dict(
    gridcolor='#1e293b',
    linecolor='#1e293b',
    tickcolor='#475569',
    color='#94a3b8'
)

# ── HEADER ──
st.markdown("<div class='hero-tag'>📦 logistics · graph ml · operations intelligence</div>",
            unsafe_allow_html=True)
st.title("Delhivery Network Operations Center")
st.markdown("""
<span class='badge'>GraphSAGE</span>
<span class='badge'>XGBoost</span>
<span class='badge'>Betweenness Centrality</span>
<span class='badge'>FTL vs Carting</span>
<br><br>
""", unsafe_allow_html=True)

# ── DATA ──
@st.cache_data
def load_data():
    df = pd.read_csv("delivery_data.csv")
    df['delay'] = df['segment_factor']
    df['od_start_time'] = pd.to_datetime(df['od_start_time'], errors='coerce')
    df['hour'] = df['od_start_time'].dt.hour
    return df

df = load_data()

# ── SIDEBAR ──
st.sidebar.markdown("### ⚙️ Control Panel")
st.sidebar.markdown("<hr style='border-color:#1e293b; margin:8px 0'>", unsafe_allow_html=True)
route_types = df['route_type'].dropna().unique().tolist()
selected_routes = st.sidebar.multiselect("Route Type", route_types, default=route_types)
delay_threshold = st.sidebar.slider("Min Delay Factor", 1.0, 3.0, 1.0, 0.1)
st.sidebar.markdown(
    "<p style='color:#475569; font-size:0.72rem; margin-top:16px; font-family:JetBrains Mono'>segment_factor > 1.0 = delayed vs OSRM</p>",
    unsafe_allow_html=True)

filtered = df[df['route_type'].isin(selected_routes) & (df['delay'] >= delay_threshold)]

st.markdown("<br>", unsafe_allow_html=True)

# ── KPI CARDS ──
col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Total Trips", f"{len(filtered):,}")
col2.metric("Avg Delay Factor", f"{filtered['delay'].mean():.2f}×")
col3.metric("Severe Delays >2×", f"{(filtered['delay']>2).sum():,}")
col4.metric("Cutoff Trips", f"{(filtered['is_cutoff']==True).sum():,}")
col5.metric("Route Types", f"{filtered['route_type'].nunique()}")

st.divider()

# ── NETWORK GRAPH ──
st.subheader("🕸️ Logistics Network — Bottleneck Analysis")
st.markdown("<p class='section-desc'>Node color intensity = betweenness centrality. Brighter nodes are structural chokepoints causing cascading delays.</p>",
            unsafe_allow_html=True)

@st.cache_data
def build_graph(_df):
    G = nx.DiGraph()
    sample = _df.sample(min(5000, len(_df)), random_state=42)
    for _, row in sample.iterrows():
        src, dst = str(row['source_name']), str(row['destination_name'])
        d = float(row['delay']) if pd.notna(row['delay']) else 1.0
        if G.has_edge(src, dst):
            G[src][dst]['weight'] = (G[src][dst]['weight'] + d) / 2
        else:
            G.add_edge(src, dst, weight=d)
    centrality = nx.betweenness_centrality(G, weight='weight', normalized=True)
    return G, centrality

with st.spinner("Computing graph centrality..."):
    G, centrality = build_graph(filtered)

pos = nx.spring_layout(G, seed=42, k=0.8)
edge_x, edge_y = [], []
for u, v in G.edges():
    x0, y0 = pos[u]; x1, y1 = pos[v]
    edge_x += [x0, x1, None]; edge_y += [y0, y1, None]

node_x = [pos[n][0] for n in G.nodes()]
node_y = [pos[n][1] for n in G.nodes()]
node_c = [centrality.get(n, 0) for n in G.nodes()]
node_txt = [f"<b>{n}</b><br>Centrality: {centrality.get(n,0):.4f}" for n in G.nodes()]

fig_net = go.Figure()
fig_net.add_trace(go.Scatter(
    x=edge_x, y=edge_y, mode='lines',
    line=dict(width=0.5, color='#1e293b'), hoverinfo='none'))
fig_net.add_trace(go.Scatter(
    x=node_x, y=node_y, mode='markers',
    marker=dict(
        size=11, color=node_c,
        colorscale=[[0,'#312e81'],[0.4,'#6366f1'],[0.7,'#f59e0b'],[1,'#ef4444']],
        showscale=True,
        colorbar=dict(
            title=dict(text="Centrality", font=dict(size=11, color='#cbd5e1')),
            thickness=12,
            tickfont=dict(size=9, color='#94a3b8'),
            bgcolor='#13172b',
            bordercolor='#1e293b'
        ),
        line=dict(width=1, color='#0d0f18')
    ),
    hovertext=node_txt, hoverinfo='text'))

fig_net.update_layout(
    **DARK_LAYOUT,
    showlegend=False, height=520,
    margin=dict(l=10, r=10, t=10, b=10),
    xaxis=dict(showgrid=False, zeroline=False, showticklabels=False,
               linecolor='#1e293b'),
    yaxis=dict(showgrid=False, zeroline=False, showticklabels=False,
               linecolor='#1e293b')
)
st.plotly_chart(fig_net, use_container_width=True)

# ── BOTTLENECK HUBS ──
st.divider()
st.subheader("🔴 Top 10 Bottleneck Hubs")
st.markdown("<p class='section-desc'>Hubs with highest betweenness centrality — responsible for most delay propagation network-wide.</p>",
            unsafe_allow_html=True)

top10 = sorted(centrality.items(), key=lambda x: x[1], reverse=True)[:10]
hub_df = pd.DataFrame(top10, columns=['Hub', 'Centrality Score'])
hub_df['Risk Level'] = ['Critical']*3 + ['High']*4 + ['Medium']*3
hub_df['Centrality Score'] = hub_df['Centrality Score'].round(4)

col_a, col_b = st.columns([1, 1.6])
with col_a:
    st.dataframe(hub_df, use_container_width=True, hide_index=True)
with col_b:
    fig_b = px.bar(hub_df, x='Hub', y='Centrality Score', color='Risk Level',
                   color_discrete_map={'Critical':'#ef4444','High':'#f59e0b','Medium':'#6366f1'},
                   text='Centrality Score')
    fig_b.update_traces(texttemplate='%{text:.3f}', textposition='outside',
                        marker_line_color='#0d0f18', marker_line_width=1)
    fig_b.update_layout(
    **DARK_LAYOUT,
    xaxis=dict(**DARK_AXIS, tickangle=30, title=''),
    yaxis=dict(**DARK_AXIS, title='Score'),
    legend=dict(orientation='h', y=-0.25, bgcolor='#13172b', bordercolor='#1e293b'),
    margin=dict(t=30, b=70)
)
    st.plotly_chart(fig_b, use_container_width=True)

st.divider()

# ── DELAY DISTRIBUTION ──
st.subheader("📊 Delay Distribution Analysis")
col_c, col_d = st.columns(2)

with col_c:
    fig_hist = px.histogram(filtered, x='delay', nbins=60,
                            title="Delay Factor Distribution",
                            labels={'delay': 'Delay Factor (actual / OSRM)'},
                            color_discrete_sequence=['#6366f1'])
    fig_hist.add_vline(x=1.0, line_dash="dot", line_color="#ef4444",
                       annotation_text="On-time baseline",
                       annotation_font=dict(color="#ef4444", size=10))
    fig_hist.update_layout(
        **DARK_LAYOUT, bargap=0.04,
        xaxis=dict(**DARK_AXIS),
        yaxis=dict(**DARK_AXIS)
    )
    st.plotly_chart(fig_hist, use_container_width=True)

with col_d:
    route_delay = filtered.groupby('route_type')['delay'].mean().reset_index()
    fig_rt = px.bar(route_delay, x='route_type', y='delay',
                    title="Avg Delay Factor by Route Type",
                    color='route_type',
                    color_discrete_sequence=['#6366f1','#f59e0b','#10b981','#ec4899'],
                    labels={'delay': 'Avg Delay Factor', 'route_type': ''})
    fig_rt.update_layout(
        **DARK_LAYOUT, showlegend=False,
        xaxis=dict(**DARK_AXIS),
        yaxis=dict(**DARK_AXIS)
    )
    st.plotly_chart(fig_rt, use_container_width=True)

# ── TOP CORRIDORS ──
st.divider()
st.subheader("🛣️ Top 15 Chronic Delay Corridors")
st.markdown("<p class='section-desc'>Only corridors with ≥5 trips included. These are structural failure points — not random outliers.</p>",
            unsafe_allow_html=True)

corridors = filtered.groupby(['source_name','destination_name'])['delay'].agg(['mean','count']).reset_index()
corridors.columns = ['Source','Destination','Avg Delay Factor','Trip Count']
corridors = corridors[corridors['Trip Count'] >= 5].nlargest(15, 'Avg Delay Factor')
corridors['Corridor'] = corridors['Source'] + ' → ' + corridors['Destination']

fig_corr = px.bar(corridors, x='Corridor', y='Avg Delay Factor',
                  color='Avg Delay Factor',
                  color_continuous_scale=[[0,'#312e81'],[0.5,'#f59e0b'],[1,'#ef4444']],
                  hover_data=['Trip Count'])
fig_corr.update_layout(
    **DARK_LAYOUT,
    xaxis=dict(**DARK_AXIS, tickangle=42, title=''),
    yaxis=dict(**DARK_AXIS, title='Avg Delay Factor'),
    margin=dict(b=130)
)
st.plotly_chart(fig_corr, use_container_width=True)

# ── HOURLY PATTERN ──
st.divider()
st.subheader("⏱️ 24-Hour Delay Pattern")
st.markdown("<p class='section-desc'>Peak delay hours indicate time-of-day congestion — actionable for scheduling and dispatch windows.</p>",
            unsafe_allow_html=True)

hourly = filtered.groupby('hour')['delay'].mean().reset_index()
fig_hour = px.area(hourly, x='hour', y='delay',
                   title="Average Delay Factor — 24hr Profile",
                   labels={'hour': 'Hour of Day', 'delay': 'Avg Delay Factor'},
                   color_discrete_sequence=['#6366f1'])
fig_hour.add_hline(y=1.0, line_dash='dot', line_color='#ef4444',
                   annotation_text='On-time baseline',
                   annotation_font=dict(color='#ef4444', size=10))
fig_hour.update_traces(line_color='#818cf8', fillcolor='rgba(99,102,241,0.15)')
fig_hour.update_layout(
    **DARK_LAYOUT,
    xaxis=dict(**DARK_AXIS, dtick=2),
    yaxis=dict(**DARK_AXIS)
)
st.plotly_chart(fig_hour, use_container_width=True)

# ── FTL vs CARTING ──
st.divider()
st.subheader("🚛 FTL vs Carting — Statistical Breakdown")
st.markdown("<p class='section-desc'>Basis for the FTL conversion decision framework. Lower mean + std = more reliable route type.</p>",
            unsafe_allow_html=True)

ftl_data = filtered.groupby('route_type')['delay'].describe().round(3).reset_index()
st.dataframe(ftl_data, use_container_width=True, hide_index=True)

st.divider()
st.caption("DELHIVERY NETWORK INTELLIGENCE  ·  GRAPH ML PROJECT  ·  2026")