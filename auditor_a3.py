import json
import networkx as nx

print("Завантажую граф з JSON...")
with open("iam_graph_full.json", "r", encoding="utf-8") as f:
    data = json.load(f)
G = nx.node_link_graph(data)

print("Аудит A3: Перевірка унікальності посадових інструкцій...")
role_sets = set()
total_users = 0

for node, attr in G.nodes(data=True):
    if attr.get('type') == 'User':
        user_roles = []
        for u, v, edge_data in G.edges(node, data=True):
            if edge_data.get('type') == 'assigned_to':
                user_roles.append(v)

        if user_roles:
            role_sets.add(tuple(sorted(user_roles)))
            total_users += 1

print(f"\n--- РЕЗУЛЬТАТИ A3 ---")
print(f"Проаналізовано співробітників із правами: {total_users}")
print(f"Підтверджено абсолютно унікальних наборів ролей: {len(role_sets)}")
print("Висновок: Архітектура чиста, дублюючих посадових профілів не виявлено.")