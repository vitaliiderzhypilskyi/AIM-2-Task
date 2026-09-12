import networkx as nx

import json

print("Завантажую граф з JSON...")
with open("iam_graph_full.json", "r", encoding="utf-8") as f:
    data = json.load(f)
G = nx.node_link_graph(data)

print("Збираю доступи для кожної ролі...")
role_grants = {}
for u, v, d in G.edges(data=True):
    if str(d.get('type')) == 'grant':
        if u not in role_grants:
            role_grants[u] = set()
        role_grants[u].add(v)

roles = list(role_grants.keys())
exact_duplicates = []
drifted_roles = []

print("Порівнюю ролі між собою (це займе пару секунд, перевіряється понад 4 мільйони пар)...")
for i in range(len(roles)):
    for j in range(i + 1, len(roles)):
        r1 = roles[i]
        r2 = roles[j]
        set1 = role_grants[r1]
        set2 = role_grants[r2]

        # Точний збіг: набори сервісів абсолютно однакові
        if set1 == set2:
            exact_duplicates.append((r1, r2))
        else:
            # Перевірка на "відхилення" (drift)
            # symmetric_difference показує унікальні сервіси, які є в одній ролі, але немає в іншій
            diff = len(set1.symmetric_difference(set2))

            # intersection показує спільну базу сервісів
            intersect = len(set1.intersection(set2))

            # Умова відхилення: ролі майже однакові (різниця не більше 2 дозволів),
            # але при цьому вони мають вагому спільну базу (мінімум 3 однакові сервіси)
            if diff <= 2 and intersect >= 3:
                drifted_roles.append((r1, r2))

print(f"\n--- РЕЗУЛЬТАТ A5 ---")
print(f"Кількість точних дублікатів: {len(exact_duplicates)}")
print(f"Кількість 'відхилених' (drifted) копій: {len(drifted_roles)}")

if exact_duplicates:
    print("\nПриклади точних дублікатів:")
    for r1, r2 in exact_duplicates[:5]:
        print(f"  {r1} <==> {r2}")

if drifted_roles:
    print("\nПриклади відхилених копій (різниця 1-2 дозволи):")
    for r1, r2 in drifted_roles[:5]:
        print(f"  {r1} ~ {r2}")