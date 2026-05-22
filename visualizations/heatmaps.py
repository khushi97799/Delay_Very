import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import os

os.makedirs("visualizations/output", exist_ok=True)

df = pd.read_csv("delivery_data.csv")
df['delay'] = df['segment_factor']

# ── Heatmap 1: Source vs Destination average delay factor ──
pivot = df.pivot_table(index='source_name', columns='destination_name',
                       values='delay', aggfunc='mean')

# Top 20x20 for readability
top_src = df.groupby('source_name')['delay'].mean().nlargest(20).index
top_dst = df.groupby('destination_name')['delay'].mean().nlargest(20).index
pivot = pivot.loc[pivot.index.isin(top_src), pivot.columns.isin(top_dst)]

plt.figure(figsize=(16, 12))
sns.heatmap(pivot, cmap='YlOrRd', linewidths=0.2,
            cbar_kws={'label': 'Avg Delay Factor (actual/OSRM)\n>1 = Delayed'},
            annot=False)
plt.title("Delay Factor Heatmap: Source → Destination\n(Top 20 highest-delay hubs)",
          fontsize=14, fontweight='bold')
plt.xticks(rotation=45, ha='right', fontsize=7)
plt.yticks(rotation=0, fontsize=7)
plt.tight_layout()
plt.savefig("visualizations/output/heatmap_corridor.png", dpi=150, bbox_inches='tight')
plt.close()
print("✅ Corridor heatmap saved.")

# ── Heatmap 2: Route type vs Source hub ──
pivot2 = df.pivot_table(index='source_name', columns='route_type',
                        values='delay', aggfunc='mean').fillna(0)
top_src2 = df.groupby('source_name')['delay'].mean().nlargest(25).index
pivot2 = pivot2.loc[pivot2.index.isin(top_src2)]

plt.figure(figsize=(10, 12))
sns.heatmap(pivot2, cmap='coolwarm', annot=True, fmt='.2f',
            cbar_kws={'label': 'Avg Delay Factor'},
            linewidths=0.3)
plt.title("Delay Factor by Hub & Route Type (FTL vs Carting)",
          fontsize=13, fontweight='bold')
plt.xticks(rotation=0)
plt.yticks(rotation=0, fontsize=7)
plt.tight_layout()
plt.savefig("visualizations/output/heatmap_routetype.png", dpi=150, bbox_inches='tight')
plt.close()
print("✅ Route type heatmap saved.")

# ── Heatmap 3: Cutoff analysis ──
df['is_cutoff'] = df['is_cutoff'].astype(str)
pivot3 = df.pivot_table(index='source_name', columns='is_cutoff',
                        values='delay', aggfunc='mean').fillna(0)
pivot3 = pivot3.loc[pivot3.index.isin(top_src2)]

plt.figure(figsize=(8, 12))
sns.heatmap(pivot3, cmap='PuRd', annot=True, fmt='.2f',
            cbar_kws={'label': 'Avg Delay Factor'}, linewidths=0.3)
plt.title("Delay Factor: Cutoff vs Non-Cutoff Shipments by Hub",
          fontsize=13, fontweight='bold')
plt.xticks(rotation=0)
plt.yticks(rotation=0, fontsize=7)
plt.tight_layout()
plt.savefig("visualizations/output/heatmap_cutoff.png", dpi=150, bbox_inches='tight')
plt.close()
print("✅ Cutoff heatmap saved.")