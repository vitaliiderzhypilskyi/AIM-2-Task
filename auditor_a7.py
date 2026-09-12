import networkx as nx
from itertools import combinations
import json

print("Завантажую граф з JSON...")
with open("iam_graph_full.json", "r", encoding="utf-8") as f:
    data = json.load(f)
G = nx.node_link_graph(data)

print("Збираю конфлікти ролей (SoD)...")
conflicts = set()
for u, v, d in G.edges(data=True):
    if str(d.get('type')) == 'conflicts_with':
        conflicts.add((u, v))
        conflicts.add((v, u))

print("Шукаю, які ролі дають доступ до яких сервісів...")
service_roles = {}
for u, v, d in G.edges(data=True):
    if str(d.get('type')) == 'grant':
        if v not in service_roles:
            service_roles[v] = set()
        service_roles[v].add(u)

print("Аналізую бізнес-процеси на наявність логічних тупиків...")
dead_workflows = []
workflows = [n for n, d in G.nodes(data=True) if str(d.get('type')) == 'Workflow']

for wf in workflows:
    steps = [v for u, v, d in G.edges(wf, data=True) if str(d.get('type')) == 'workflow_step']
    is_dead = False

    for srv1, srv2 in combinations(steps, 2):
        if srv1 not in service_roles or srv2 not in service_roles:
            continue

        for r1 in service_roles[srv1]:
            for r2 in service_roles[srv2]:
                if (r1, r2) in conflicts:
                    dead_workflows.append((wf, srv1, srv2, r1, r2))
                    is_dead = True
                    break
            if is_dead: break
        if is_dead: break

print(f"\n--- РЕЗУЛЬТАТ A7 ---")
print(f"Кількість 'мертвих' бізнес-процесів: {len(dead_workflows)}")
if dead_workflows:
    print("\nПриклади неможливих процесів:")
    for wf, srv1, srv2, r1, r2 in dead_workflows[:5]:
        print(f"  {wf} заблоковано через конфлікт.")
        print(f"  Механізм: Крок {srv1} вимагає роль {r1}, а Крок {srv2} вимагає {r2}.")
else:
    print("Висновок: Логічних тупиків не знайдено (всі процеси можуть бути виконані безпечно).")