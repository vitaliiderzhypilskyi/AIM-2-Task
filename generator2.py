import networkx as nx
import random
import copy
import json

def create_iam_graph(scale='full'):
    # scale='full' - для великого графа (скриптовий аудит).
    # scale='small' - для малого графа (візуальний аудит в Gephi).
    G = nx.DiGraph()

    # 1. Налаштування параметрів (рандомізація без жорстких чисел)
    if scale == 'full':
        num_srv = random.randint(8500, 10000)
        num_usr = random.randint(1800, 2200)
        num_rol = random.randint(2500, 3000)
        num_jobs = random.randint(55, 75)
        num_wf = random.randint(250, 350)
    else:  # small для Gephi
        num_srv = random.randint(50, 70)
        num_usr = random.randint(15, 20)
        num_rol = random.randint(20, 30)
        num_jobs = random.randint(3, 5)
        num_wf = random.randint(5, 10)

    services = [f"Service_{i}" for i in range(num_srv)]
    users = [f"User_{i}" for i in range(num_usr)]
    roles = [f"Role_{i}" for i in range(num_rol)]
    workflows = [f"Workflow_{i}" for i in range(num_wf)]

    # Додаємо вузли
    G.add_nodes_from(services, type='Service', label=services)
    G.add_nodes_from(users, type='User', label=users)
    G.add_nodes_from(roles, type='Role', label=roles)
    G.add_nodes_from(workflows, type='Workflow', label=workflows)

    print(f"[{scale.upper()}] Генеруємо {num_srv} сервісів, {num_rol} ролей, {num_usr} юзерів...")

    # ==========================================
    # A3, A5: Role Drift (Еталонні ролі, дублікати та розмиття)
    # ==========================================
    role_grants = {}
    base_roles_count = int(num_rol * 0.8)
    base_roles = roles[:base_roles_count]
    clone_roles = roles[base_roles_count:]

    # 1. Створюємо еталонні ролі
    for role in base_roles:
        grants = set(random.sample(services, k=random.randint(3 if scale == 'small' else 5, 15)))
        role_grants[role] = grants
        for srv in grants:
            G.add_edge(role, srv, type='grant')

    # 2. Створюємо клони (для A5)
    for role in clone_roles:
        target_base = random.choice(base_roles)
        grants = copy.deepcopy(role_grants[target_base])

        # 50% шанс, що це точний дублікат, 50% - Role Drift (розмиття)
        if random.random() > 0.5:
            if grants: grants.pop()
            grants.add(random.choice(services))

        role_grants[role] = grants
        for srv in grants:
            G.add_edge(role, srv, type='grant')

    # ==========================================
    # A2: Посади (Job Functions) та Шум (Noise)
    # ==========================================
    job_profiles = [random.sample(roles, k=random.randint(2 if scale == 'small' else 10, 20)) for _ in range(num_jobs)]
    user_roles_map = {}

    for user in users:
        base_profile = random.choice(job_profiles)
        actual_roles = set(base_profile)

        if random.random() > 0.5 and actual_roles: actual_roles.pop()
        if random.random() > 0.5: actual_roles.add(random.choice(roles))

        # ==========================================
        # A6: Shadow IT (Чесне, без чітерських тегів)
        # ==========================================
        if random.random() < (0.1 if scale == 'small' else 0.03):
            shadow_role = random.choice(roles)
            actual_roles.add(shadow_role)

        user_roles_map[user] = actual_roles
        for role in actual_roles:
            G.add_edge(user, role, type='assigned_to')

    # ==========================================
    # A4: Сміттєві доступи (Винятки / Exceptions)
    # ==========================================
    num_exceptions = 3 if scale == 'small' else int(num_usr * 0.05)
    for user in random.sample(users, k=num_exceptions):
        G.add_edge(user, random.choice(services), type='direct_grant')

    # ==========================================
    # A1: Взаємодія сервісів та Випадкова Кліка
    # ==========================================
    calls_count = 20 if scale == 'small' else random.randint(1500, 2500)
    for srv in random.sample(services, k=min(calls_count, len(services))):
        for t in random.sample(services, k=random.randint(1, 3)):
            if srv != t:
                G.add_edge(srv, t, type='calls')

    clique_size = random.randint(4, 6) if scale == 'small' else random.randint(10, 20)
    clique_services = random.sample(services, k=clique_size)
    for s1 in clique_services:
        for s2 in clique_services:
            if s1 != s2:
                G.add_edge(s1, s2, type='calls')

    # ==========================================
    # A7: Workflows та SoD (Segregation of Duties)
    # ==========================================
    for wf in workflows:
        wf_steps = random.sample(services, k=random.randint(3 if scale == 'small' else 5, 8 if scale == 'small' else 15))
        for i, step_srv in enumerate(wf_steps):
            G.add_edge(wf, step_srv, type='workflow_step', step_index=i)

    # Створюємо SoD конфлікти
    num_sod = 5 if scale == 'small' else 50
    for _ in range(num_sod):
        r1, r2 = random.sample(roles, 2)
        G.add_edge(r1, r2, type='sod_conflict')

    # Штучно ламаємо кілька Workflows (БАГ З ВІДСТУПОМ ВИПРАВЛЕНО ТУТ)
    dead_wfs = random.sample(workflows, k=2 if scale == 'small' else 20)
    for wf in dead_wfs:
        steps = [v for u, v, d in G.edges(wf, data=True) if d.get('type') == 'workflow_step']
        if len(steps) >= 2:
            s1, s2 = steps[0], steps[1]

            roles_s1 = [u for u, v, d in G.in_edges(s1, data=True) if d.get('type') == 'grant']
            roles_s2 = [u for u, v, d in G.in_edges(s2, data=True) if d.get('type') == 'grant']

            if roles_s1 and roles_s2:
                for r1 in roles_s1:
                    for r2 in roles_s2:
                        G.add_edge(r1, r2, type='sod_conflict')

    # ==========================================
    # ЕКСПОРТ У JSON
    # ==========================================
    output_file = f"iam_graph_{scale}.json"
    data = nx.node_link_data(G)

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    print(f"[{scale.upper()}] Збережено в {output_file} (Вузлів: {G.number_of_nodes()}, Ребер: {G.number_of_edges()})\n")

if __name__ == "__main__":
    create_iam_graph(scale='small')
    create_iam_graph(scale='full')
    print("Генерація успішно завершена! Ви маєте два файли: iam_graph_small.json та iam_graph_full.json")