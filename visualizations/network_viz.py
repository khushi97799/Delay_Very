import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import os
import json

os.makedirs("visualizations/output", exist_ok=True)

df = pd.read_csv("delivery_data.csv")
df['delay'] = df['segment_factor']

# Build directed graph
G = nx.DiGraph()
for _, row in df.iterrows():
    src = str(row['source_name'])
    dst = str(row['destination_name'])
    delay = float(row['delay']) if pd.notna(row['delay']) else 1.0
    if G.has_edge(src, dst):
        G[src][dst]['weight'] = (G[src][dst]['weight'] + delay) / 2
    else:
        G.add_edge(src, dst, weight=delay)

# Compute betweenness centrality
print("Computing centrality (may take 30s)...")
centrality = nx.betweenness_centrality(G, weight='weight', normalized=True)
nx.set_node_attributes(G, centrality, 'centrality')

# Top 5 bottleneck hubs
top5 = sorted(centrality.items(), key=lambda x: x[1], reverse=True)[:5]
print("\n🔴 Top 5 Bottleneck Hubs:")
for hub, score in top5:
    print(f"  {hub}: {score:.4f}")

with open("visualizations/top5_hubs.json", "w") as f:
    json.dump(top5, f)

# Subgraph: top 80 nodes
top_nodes = [n for n, _ in sorted(centrality.items(), key=lambda x: x[1], reverse=True)[:80]]
H = G.subgraph(top_nodes)

node_list = list(H.nodes())
cent_values = [centrality.get(n, 0) for n in node_list]

# ── FIX: use fig, ax properly ──
fig, ax = plt.subplots(figsize=(18, 12))

norm = mcolors.Normalize(vmin=min(cent_values), vmax=max(cent_values))
cmap = plt.cm.RdYlGn_r
colors = [cmap(norm(v)) for v in cent_values]

pos = nx.spring_layout(H, seed=42, k=1.2)

nx.draw_networkx_nodes(H, pos, nodelist=node_list, node_color=colors,
                       node_size=300, alpha=0.9, ax=ax)
nx.draw_networkx_labels(H, pos, font_size=6, ax=ax)
nx.draw_networkx_edges(H, pos, alpha=0.2, arrows=True,
                       arrowstyle='->', arrowsize=8, ax=ax)

# ── FIX: attach colorbar to ax ──
sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
sm.set_array([])
fig.colorbar(sm, ax=ax, label='Betweenness Centrality (Bottleneck Score)')

ax.set_title("Delhivery Logistics Network — Bottleneck Hub Analysis\n(Red = High Risk, Green = Low Risk)",
             fontsize=14, fontweight='bold')
ax.axis('off')
plt.tight_layout()
plt.savefig("visualizations/output/network_graph.png", dpi=150, bbox_inches='tight')
plt.close()
print("\n✅ Network graph saved to visualizations/output/network_graph.png")