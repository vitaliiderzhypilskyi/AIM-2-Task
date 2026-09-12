import networkx as nx
import json

print("Завантажую граф з JSON...")
with open("iam_graph_full.json", "r", encoding="utf-8") as f:
    data = json.load(f)
G = nx.node_link_graph(data)

print("Шукаю ролі, які легально закріплені за відновленими посадами...")
official_roles = set()
for u, v, d in G.edges(data=True):
    if str(d.get('type')) == 'assigned_to':
        official_roles.add(v)  # v = Role

print("Аналізую всі права доступу на наявність винятків...")
exceptions = []
for u, v, d in G.edges(data=True):
    if str(d.get('type')) == 'grant':  # u = Role, v = Service
        # Якщо роль, яка дає доступ, ніколи нікому не видавалась офіційно:
        if u not in official_roles:
            exceptions.append((u, v))

print(f"\n--- РЕЗУЛЬТАТ A4 ---")
print(f"Кількість 'сміттєвих' дозволів-винятків: {len(exceptions)}")
if exceptions:
    print("Приклади таких дозволів (перші 15):")
    for role_id, srv_id in exceptions[:15]:
        print(f"  {role_id} -> {srv_id}")
    print("  ... і так далі.")