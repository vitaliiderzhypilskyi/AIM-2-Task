import json
import networkx as nx


def analyze_a3_job_functions(file_path="iam_graph_full.json"):
    print(f"Завантажую граф з {file_path}...")
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        G = nx.node_link_graph(data)
    except Exception as e:
        print(f"Помилка завантаження: {e}")
        return

    print("Аудит A3: Вираховую кількість реальних посадових профілів (кластеризація ролей)...")

    # 1. Збираємо ролі (assigned_to) для кожного юзера
    user_roles = {}
    for node, attr in G.nodes(data=True):
        if attr.get('type') == 'User':
            roles = set()
            for u, v, edata in G.out_edges(node, data=True):
                if edata.get('type') == 'assigned_to':
                    roles.add(v)
            if roles:
                user_roles[node] = roles

    # 2. Кластеризація на основі подібності Жаккара
    # Поріг 0.75 дозволяє згрупувати юзерів в одну посаду, навіть якщо у них відрізняється 1-2 ролі
    threshold = 0.75
    clusters = []

    for user, roles in user_roles.items():
        placed = False
        for cluster in clusters:
            centroid_roles = user_roles[cluster[0]]

            intersection = len(roles.intersection(centroid_roles))
            union = len(roles.union(centroid_roles))
            jaccard = intersection / union if union > 0 else 0

            if jaccard >= threshold:
                cluster.append(user)
                placed = True
                break

        if not placed:
            clusters.append([user])

    # Кількість кластерів = кількість реальних посадових функцій (Job Functions)
    distinct_job_functions = len(clusters)

    print(f"\n--- РЕЗУЛЬТАТИ A3 ---")
    print(f"Проаналізовано співробітників: {len(user_roles)}")
    print(f"Кількість виявлених унікальних посадових функцій (кластерів): {distinct_job_functions}")
    print(
        "Висновок: Значення вираховано математично на основі перетину множин ролей, ігноруючи індивідуальні відхилення.")


if __name__ == "__main__":
    # analyze_a3_job_functions("iam_graph_full.json")
    analyze_a3_job_functions("iam_graph_small.json")
