import networkx as nx
import json
from itertools import combinations

def analyze_a7_dead_workflows(file_path="iam_graph_small.json"):
    print(f"Завантажую граф з {file_path}...")
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        G = nx.node_link_graph(data)
    except Exception as e:
        print(f"Помилка завантаження файлу: {e}")
        return

    print("Аудит A7: Аналізую бізнес-процеси (SoD та BoD)...")

    conflicts = set()
    role_users = {}
    service_roles = {}

    # Збираємо всі необхідні зв'язки з графа
    for u, v, d in G.edges(data=True):
        edge_type = str(d.get('type'))
        if edge_type == 'sod_conflict':
            conflicts.add((u, v))
            conflicts.add((v, u))
        elif edge_type == 'grant':
            if v not in service_roles:
                service_roles[v] = set()
            service_roles[v].add(u)
        elif edge_type == 'assigned_to':
            # u = User, v = Role
            if v not in role_users:
                role_users[v] = set()
            role_users[v].add(u)

    # ТРИ КАТЕГОРІЇ ПОМИЛОК
    dead_by_sod = []
    dead_by_missing_role = []
    dead_by_bod = []  # Нова категорія для Binding of Duties

    workflows = [n for n, d in G.nodes(data=True) if str(d.get('type')) == 'Workflow']

    for wf in workflows:
        steps = [v for u, v, d in G.out_edges(wf, data=True) if str(d.get('type')) == 'workflow_step']

        has_sod = False
        has_bod = False
        sod_details = None
        bod_details = None
        missing_details = None

        for srv1, srv2 in combinations(steps, 2):
            roles1 = service_roles.get(srv1, set())
            roles2 = service_roles.get(srv2, set())

            # 1. Архітектурний тупик
            if not roles1 or not roles2:
                if not missing_details:
                    missing_details = (srv1, srv2)
                continue

            # 2. Перевірка SoD (Конфлікт політик)
            all_blocked_by_sod = True
            for r1 in roles1:
                for r2 in roles2:
                    if (r1, r2) not in conflicts:
                        all_blocked_by_sod = False
                        break
                if not all_blocked_by_sod:
                    break

            if all_blocked_by_sod:
                has_sod = True
                sod_details = (srv1, srv2, list(roles1)[0], list(roles2)[0])
                break  # SoD має найвищий пріоритет, далі можна не шукати

            # 3. Перевірка BoD (Відсутність виконавця)
            # Збираємо всіх юзерів, які мають доступ до srv1
            users_srv1 = set()
            for r in roles1:
                users_srv1.update(role_users.get(r, set()))

            # Збираємо всіх юзерів, які мають доступ до srv2
            users_srv2 = set()
            for r in roles2:
                users_srv2.update(role_users.get(r, set()))

            # Шукаємо перетин (чи є хоч одна людина, яка має доступ до обох)
            common_users = users_srv1.intersection(users_srv2)

            if not common_users:
                has_bod = True
                bod_details = (srv1, srv2)
                # Продовжуємо цикл: можливо, для іншої пари кроків знайдеться жорсткіший SoD конфлікт

        # Розподіляємо по категоріях
        if has_sod:
            dead_by_sod.append((wf, *sod_details))
        elif has_bod:
            dead_by_bod.append((wf, *bod_details))
        elif missing_details:
            dead_by_missing_role.append((wf, *missing_details))

    print(f"\n--- РЕЗУЛЬТАТ A7 ---")
    total_dead = len(dead_by_sod) + len(dead_by_missing_role) + len(dead_by_bod)
    print(f"Всього 'мертвих' процесів знайдено: {total_dead}")
    print(f" З них через конфлікт інтересів (SoD): {len(dead_by_sod)}")
    print(f" З них через відсутність виконавця (BoD): {len(dead_by_bod)}")
    print(f" З них через архітектурні помилки (немає ролей до сервісів): {len(dead_by_missing_role)}")

    if dead_by_sod:
        print("\n--- ПРИКЛАДИ SoD КОНФЛІКТІВ (Політика безпеки) ---")
        for wf, srv1, srv2, r1, r2 in dead_by_sod[:5]:
            print(f"  {wf} заблоковано. Крок {srv1} вимагає {r1}, а {srv2} вимагає {r2} (Конфлікт SoD!)")

    if dead_by_bod:
        print("\n--- ПРИКЛАДИ BoD БЛОКУВАНЬ (Відсутність виконавця) ---")
        for wf, srv1, srv2 in dead_by_bod[:5]:
            print(f"  {wf} заблоковано. Жоден користувач у системі не має доступу одночасно до {srv1} та {srv2}.")

    if dead_by_missing_role:
        print("\n--- ПРИКЛАДИ АРХІТЕКТУРНИХ ТУПИКІВ (Осиротілі сервіси) ---")
        for wf, srv1, srv2 in dead_by_missing_role[:5]:
            print(f"  {wf} заблоковано: відсутні ролі для доступу до {srv1} або {srv2}.")


if __name__ == "__main__":
    analyze_a7_dead_workflows("iam_graph_small.json")
    # analyze_a7_dead_workflows("iam_graph_full.json")
