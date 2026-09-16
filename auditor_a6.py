import networkx as nx
import json


def analyze_a6_shadow_it(file_path="iam_graph_full.json"):
    print(f"Завантажую граф з {file_path}...")
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        G = nx.node_link_graph(data)
    except Exception as e:
        print(f"Помилка завантаження файлу: {e}")
        return

    print("Аудит A6: Проводжу Peer Group Analysis (пошук аномалій серед колег)...")

    # 1. Збираємо всі офіційні ролі (assigned_to) для кожного юзера
    user_roles = {}
    for node, attr in G.nodes(data=True):
        if attr.get('type') == 'User':
            roles = {v for u, v, d in G.out_edges(node, data=True) if d.get('type') == 'assigned_to'}
            if roles:
                user_roles[node] = roles

    violating_users = set()
    shadow_roles_found = 0

    # 2. Математичний пошук викидів
    for u, roles in user_roles.items():
        # Шукаємо "колег" - тих, у кого збіг ролей більше 50%
        peers = []
        for v, v_roles in user_roles.items():
            if u == v:
                continue
            intersection = len(roles.intersection(v_roles))
            union = len(roles.union(v_roles))

            # Якщо профіль збігається більш ніж наполовину - це колега по посаді
            if union > 0 and (intersection / union) > 0.5:
                peers.append(v)

        # Якщо у юзера немає колег, ми не можемо достовірно оцінити аномалію
        if not peers:
            continue

        # Збираємо "Еталонний набір ролей" - усі ролі, якими володіють колеги
        peer_roles = set()
        for p in peers:
            peer_roles.update(user_roles[p])

        # 3. Перевірка на Shadow IT
        # Якщо юзер має роль, яка не зустрічається у жодного з колег -> це аномалія
        for r in roles:
            if r not in peer_roles:
                violating_users.add(u)
                shadow_roles_found += 1
                break  # Однієї тіньової ролі достатньо, щоб вважати юзера порушником

    print(f"\n--- РЕЗУЛЬТАТ A6 ---")
    print(f"Кількість користувачів із 'тіньовими' ролями (поза профілем): {len(violating_users)}")
    print(f"Загалом виявлено аномальних призначень: {shadow_roles_found}")

    if violating_users:
        violating_list = sorted(list(violating_users))
        print(f"ID користувачів-порушників (перші 15): {', '.join(violating_list[:15])}")


if __name__ == "__main__":
 # analyze_a6_shadow_it("iam_graph_full.json")
 analyze_a6_shadow_it("iam_graph_small.json")
