import networkx as nx
import json
from itertools import combinations


def analyze_a7_dead_workflows(file_path="iam_graph_full.json"):
    print(f"Завантажую граф з {file_path}...")
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        G = nx.node_link_graph(data)
    except Exception as e:
        print(f"Помилка завантаження файлу: {e}")
        return

    print("Аудит A7: Аналізую бізнес-процеси...")

    conflicts = set()
    for u, v, d in G.edges(data=True):
        if str(d.get('type')) == 'sod_conflict':
            conflicts.add((u, v))
            conflicts.add((v, u))

    service_roles = {}
    for u, v, d in G.edges(data=True):
        if str(d.get('type')) == 'grant':
            if v not in service_roles:
                service_roles[v] = set()
            service_roles[v].add(u)

    # ДВІ КАТЕГОРІЇ ПОМИЛОК
    dead_by_sod = []
    dead_by_missing_role = []

    workflows = [n for n, d in G.nodes(data=True) if str(d.get('type')) == 'Workflow']

    for wf in workflows:
        steps = [v for u, v, d in G.out_edges(wf, data=True) if str(d.get('type')) == 'workflow_step']

        has_sod = False
        sod_details = None
        missing_details = None

        for srv1, srv2 in combinations(steps, 2):
            roles1 = service_roles.get(srv1, set())
            roles2 = service_roles.get(srv2, set())

            # Якщо ролей немає, запам'ятовуємо, але продовжуємо шукати SoD
            if not roles1 or not roles2:
                if not missing_details:
                    missing_details = (srv1, srv2)
                continue

            all_blocked = True
            for r1 in roles1:
                for r2 in roles2:
                    if (r1, r2) not in conflicts:
                        all_blocked = False
                        break
                if not all_blocked:
                    break

            if all_blocked:
                has_sod = True
                sod_details = (srv1, srv2, list(roles1)[0], list(roles2)[0])
                break  # Знайшли SoD - це найвищий пріоритет, зупиняємось для цього WF

        # Розподіляємо по категоріях
        if has_sod:
            dead_by_sod.append((wf, *sod_details))
        elif missing_details:
            dead_by_missing_role.append((wf, *missing_details))

    print(f"\n--- РЕЗУЛЬТАТ A7 ---")
    print(f"Всього 'мертвих' процесів знайдено: {len(dead_by_sod) + len(dead_by_missing_role)}")
    print(f" З них через конфлікт інтересів (SoD): {len(dead_by_sod)}")
    print(f" З них через архітектурні помилки (немає ролей до сервісів): {len(dead_by_missing_role)}")

    if dead_by_sod:
        print("\n--- ПРИКЛАДИ SoD КОНФЛІКТІВ (Політика безпеки) ---")
        for wf, srv1, srv2, r1, r2 in dead_by_sod[:5]:
            print(f"  {wf} заблоковано. Крок {srv1} вимагає {r1}, а Крок {srv2} вимагає {r2} (Конфлікт!)")

    if dead_by_missing_role:
        print("\n--- ПРИКЛАДИ АРХІТЕКТУРНИХ ТУПИКІВ (Осиротілі сервіси) ---")
        for wf, srv1, srv2 in dead_by_missing_role[:5]:
            print(f"  {wf} заблоковано: відсутні будь-які ролі для доступу до {srv1} або {srv2}.")


if __name__ == "__main__":
    # analyze_a7_dead_workflows("iam_graph_full.json")
    analyze_a7_dead_workflows("iam_graph_small.json")
