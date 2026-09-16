import json
import networkx as nx


def analyze_a2_clustering(file_path="iam_graph_full.json"):
    print(f"Завантажую граф з {file_path}...")
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        G = nx.node_link_graph(data)
    except Exception as e:
        print(f"Помилка завантаження: {e}")
        return

    print("Аудит A2: Шукаємо блоки користувачів за подібністю сервісів...")

    # 1. Збираємо унікальні сервіси для кожного юзера
    user_services = {}
    for node, attr in G.nodes(data=True):
        if attr.get('type') == 'User':
            services = set()

            # Шукаємо доступи (як через ролі, так і прямі для A4)
            for u, v, edata in G.out_edges(node, data=True):
                edge_type = edata.get('type')

                # Якщо це прямий доступ (Exceptions)
                if edge_type == 'direct_grant' and G.nodes[v].get('type') == 'Service':
                    services.add(v)

                # Якщо це роль, ідемо на глибину +1 до сервісів
                elif edge_type == 'assigned_to':
                    role = v
                    for r, srv, grant_data in G.out_edges(role, data=True):
                        if grant_data.get('type') == 'grant' and G.nodes[srv].get('type') == 'Service':
                            services.add(srv)

            if services:
                user_services[node] = services

    print(f"Зібрано дані для {len(user_services)} користувачів. Починаю кластеризацію (Jaccard >= 0.85)...")

    # 2. Наближена кластеризація (Жаккар)
    clusters = []
    for user, services in user_services.items():
        placed = False
        for cluster in clusters:
            # Беремо першого юзера кластера як "центроїд" (еталон)
            centroid_user = cluster[0]
            centroid_services = user_services[centroid_user]

            # Формула Жаккара: (Перетин / Об'єднання)
            intersection = len(services.intersection(centroid_services))
            union = len(services.union(centroid_services))
            jaccard = intersection / union if union > 0 else 0

            # Якщо збіг більше 85% — це одна посада (Job Function)
            if jaccard >= 0.85:
                cluster.append(user)
                placed = True
                break

        if not placed:
            clusters.append([user])

    print(f"Сформовано {len(clusters)} груп. Рахую максимальний Score...")

    # 3. Знаходимо блок-переможець
    winning_score = 0
    winning_users_count = 0
    winning_services_count = 0
    winning_service_ids = []

    for cluster in clusters:
        if len(cluster) < 2:
            continue  # Ігноруємо одиноких користувачів

        # Шукаємо "ядро": сервіси, які є гарантовано у КОЖНОГО члена групи (перетин)
        shared_services = set(user_services[cluster[0]])
        for user in cluster[1:]:
            shared_services.intersection_update(user_services[user])

        user_count = len(cluster)
        service_count = len(shared_services)
        score = user_count * service_count

        if score > winning_score:
            winning_score = score
            winning_users_count = user_count
            winning_services_count = service_count
            winning_service_ids = sorted(list(shared_services))

    print(f"\n--- РЕЗУЛЬТАТИ A2 ---")
    print(f"Кількість користувачів у найкращому блоці: {winning_users_count}")
    print(f"Кількість спільних сервісів: {winning_services_count}")
    print(f"Оцінка блоку (Score = {winning_users_count} * {winning_services_count}): {winning_score}")

    if winning_services_count > 0:
        show_services = winning_service_ids[:15]  # Виводимо перші 15 для краси
        suffix = "..." if len(winning_service_ids) > 15 else ""
        print(f"ID сервісів: {', '.join(show_services)}{suffix}")


if __name__ == "__main__":
    # analyze_a2_clustering("iam_graph_full.json")
    analyze_a2_clustering("iam_graph_small.json")
