import networkx as nx
import json


def analyze_a5_role_drift(file_path="iam_graph_full.json"):
    print(f"Завантажую граф з {file_path}...")
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        G = nx.node_link_graph(data)
    except Exception as e:
        print(f"Помилка завантаження файлу: {e}")
        return

    print("Аудит A5: Збираю доступи для кожної ролі...")
    role_grants = {}
    for u, v, d in G.edges(data=True):
        if str(d.get('type')) == 'grant':
            if u not in role_grants:
                role_grants[u] = set()
            role_grants[u].add(v)

    roles = list(role_grants.keys())
    exact_duplicates = []
    drifted_roles = []

    print(f"Порівнюю {len(roles)} ролей (шукаю симетричну різницю множин)...")

    # Попарне порівняння O(N^2)
    for i in range(len(roles)):
        for j in range(i + 1, len(roles)):
            r1 = roles[i]
            r2 = roles[j]
            set1 = role_grants[r1]
            set2 = role_grants[r2]

            # Точний збіг
            if set1 == set2:
                exact_duplicates.append((r1, r2))
            else:
                # Відхилення (Role Drift)
                # diff: скільки унікальних сервісів розрізняють ці дві ролі
                diff = len(set1.symmetric_difference(set2))

                # intersect: скільки спільних сервісів вони мають
                intersect = len(set1.intersection(set2))

                # Умова: різниця максимум 2 дозволи, але база мінімум 3 дозволи
                if diff <= 2 and intersect >= 3:
                    drifted_roles.append((r1, r2))

    print(f"\n--- РЕЗУЛЬТАТ A5 ---")
    print(f"Кількість точних дублікатів: {len(exact_duplicates)}")
    print(f"Кількість 'мутованих' (drifted) копій: {len(drifted_roles)}")

    if exact_duplicates:
        print("\nПриклади точних дублікатів (перші 5):")
        for r1, r2 in exact_duplicates[:5]:
            print(f"  {r1} <==> {r2}")

    if drifted_roles:
        print("\nПриклади відхилених копій (різниця 1-2 дозволи):")
        for r1, r2 in drifted_roles[:5]:
            print(f"  {r1} ~ {r2}")


if __name__ == "__main__":
    # analyze_a5_role_drift("iam_graph_full.json")
    analyze_a5_role_drift("iam_graph_small.json")
