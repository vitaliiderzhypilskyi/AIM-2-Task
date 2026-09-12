import networkx as nx
import json

print("Завантажую граф з JSON...")
with open("iam_graph_full.json", "r", encoding="utf-8") as f:
    data = json.load(f)
G = nx.node_link_graph(data)

print("Шукаю порушників (Shadow IT)...")
violating_users = set()

# Шукаємо всі зв'язки типу 'shadow_role' (роль, видана напряму в обхід посади)
for u, v, d in G.edges(data=True):
    if str(d.get('type')) == 'shadow_role':
        violating_users.add(u)  # u = User

print(f"\n--- РЕЗУЛЬТАТ A6 ---")
print(f"Кількість користувачів із 'тіньовими' ролями: {len(violating_users)}")
if violating_users:
    violating_list = sorted(list(violating_users))
    print(f"ID користувачів (перші 15): {', '.join(violating_list[:15])}")