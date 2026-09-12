import networkx as nx

import json

print("Завантажую граф з JSON...")
with open("iam_graph_full.json", "r", encoding="utf-8") as f:
    data = json.load(f)
G = nx.node_link_graph(data)

print("Аналізую взаємодію між сервісами...")
# Створюємо новий порожній граф, куди додамо ТІЛЬКИ ідеальні двосторонні зв'язки
mutual_G = nx.Graph()

# Збираємо всі виклики між сервісами у швидку пам'ять (множину)
calls = set()
for u, v, data in G.edges(data=True):
    if data.get('type') == 'calls':
        calls.add((u, v))

print("Фільтрую односторонні виклики...")
# Залишаємо лише ті зв'язки, де є виклик і туди, і назад
for u, v in calls:
    if (v, u) in calls and u != v:
        mutual_G.add_edge(u, v)

print("Шукаю найбільшу повністю зв'язну групу (максимальну кліку)...")
# Алгоритм Брона-Кербоша знаходить усі максимальні кліки
cliques = list(nx.find_cliques(mutual_G))

if not cliques:
    print("Взаємних груп не знайдено.")
else:
    largest_clique = max(cliques, key=len)
    print(f"\n--- РЕЗУЛЬТАТ A1 ---")
    print(f"Розмір найбільшої групи: {len(largest_clique)}")
    print(f"ID сервісів: {', '.join(sorted(largest_clique))}")