import networkx as nx
import json

print("Читаю JSON...")
with open("iam_graph_full.json", "r", encoding="utf-8") as f:
    data = json.load(f)

G = nx.node_link_graph(data)

print("Очищаю атрибути для сумісності з GraphML...")
# Проходимося по всіх вузлах і виправляємо списки
for node, attrs in G.nodes(data=True):
    # Встановлюємо ім'я вузла як його label для Gephi
    attrs['label'] = str(node)
    for key, val in list(attrs.items()):
        if isinstance(val, (list, dict)):
            attrs[key] = str(val)

# Проходимося по всіх зв'язках
for u, v, attrs in G.edges(data=True):
    for key, val in list(attrs.items()):
        if isinstance(val, (list, dict)):
            attrs[key] = str(val)

print("Конвертую для Gephi...")
nx.write_graphml(G, "iam_graph_for_gephi.graphml")
print("Готово! Відкривай iam_graph_for_gephi.graphml у Gephi.")