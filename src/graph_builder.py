import networkx as nx
import pandas as pd

df = pd.read_csv(
    "data/processed/cleaned_data.csv"
)

G = nx.DiGraph()

for _, row in df.iterrows():

    source = row['source_center']
    destination = row['destination_center']

    delay_ratio = row['delay_ratio']

    G.add_edge(
        source,
        destination,
        weight=delay_ratio
    )

print(
    "Number of nodes:",
    G.number_of_nodes()
)

print(
    "Number of edges:",
    G.number_of_edges()
)

degree = dict(G.degree())

betweenness = nx.betweenness_centrality(G)

pagerank = nx.pagerank(G)

clustering = nx.clustering(
    G.to_undirected()
)

df['source_degree'] = (
    df['source_center'].map(degree)
)

df['source_betweenness'] = (
    df['source_center'].map(betweenness)
)

df['source_pagerank'] = (
    df['source_center'].map(pagerank)
)

df['source_clustering'] = (
    df['source_center'].map(clustering)
)

df.to_csv(
    "data/processed/final_data.csv",
    index=False
)