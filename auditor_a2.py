import json
import networkx as nx
from collections import defaultdict

print("Завантажую граф з JSON...")
with open("iam_graph_full.json", "r", encoding="utf-8") as f:
    data = json.load(f)
G = nx.node_link_graph(data)

print("Аудит A2: Відновлення посад (Role Mining)...")
job_clusters = defaultdict(list)

for node, attr in G.nodes(data=True):
    if attr.get('type') == 'User':
        user_roles = []
        for u, v, edge_data in G.edges(node, data=True):
            if edge_data.get('type') == 'assigned_to':
                user_roles.append(v)

        if user_roles:
            role_signature = tuple(sorted(user_roles))
            job_clusters[role_signature].append(node)

print(f"\n--- РЕЗУЛЬТАТИ A2 ---")
print(f"Знайдено унікальних патернів (відновлених посад): {len(job_clusters)}")

largest_cluster = max(job_clusters.values(), key=len)
print(f"Найбільша група: {len(largest_cluster)} співробітників виконують ідентичну роботу.")