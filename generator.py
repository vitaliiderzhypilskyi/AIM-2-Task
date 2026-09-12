import networkx as nx
import random
import json


def generate_full_graph():
    G = nx.DiGraph()

    # 1. Випадкова генерація кількості сутностей (щоб не було рівно 60 посад)
    num_services = random.randint(8500, 10000)
    num_users = random.randint(1800, 2200)
    num_roles = random.randint(2500, 3000)
    num_implicit_jobs = random.randint(55, 75)  # Приховані посади (лише для логіки)
    num_workflows = random.randint(250, 350)

    services = [f"Service_{i}" for i in range(num_services)]
    users = [f"User_{i}" for i in range(num_users)]
    roles = [f"Role_{i}" for i in range(num_roles)]
    workflows = [f"Workflow_{i}" for i in range(num_workflows)]

    print("Додаю базові вузли (Користувачі, Ролі, Сервіси, Воркфлоу)...")
    G.add_nodes_from(services, type='Service', label=services)
    G.add_nodes_from(users, type='User', labeІl=users)
    G.add_nodes_from(roles, type='Role', label=roles)
    G.add_nodes_from(workflows, type='Workflow', label=workflows)

    print("Генерую базові дозволи (Role -> Service)...")
    for role in roles:
        for srv in random.sample(services, k=random.randint(5, 15)):
            G.add_edge(role, srv, type='grant')

    print(f"Генерую патерни для {num_implicit_jobs} прихованих посад...")
    # 2. Створюємо шаблони посад, але НЕ додаємо їх у граф як вузли
    job_profiles = []
    for _ in range(num_implicit_jobs):
        profile_roles = random.sample(roles, k=random.randint(10, 30))
        job_profiles.append(profile_roles)

    print("Призначаю користувачам ролі на основі прихованих патернів...")
    # 3. Користувачі отримують ролі напряму. Посад у графі більше немає.
    user_profiles = {}
    for user in users:
        profile = random.choice(job_profiles)
        user_profiles[user] = profile
        for role in profile:
            G.add_edge(user, role, type='assigned_to')

    print("Додаю взаємодію між сервісами (для A1)...")
    for srv in random.sample(services, k=1500):
        for t in random.sample(services, k=random.randint(1, 3)):
            if srv != t:
                G.add_edge(srv, t, type='calls')

    # Штучна кліка для A1
    clique_services = random.sample(services, k=8)
    for s1 in clique_services:
        for s2 in clique_services:
            if s1 != s2:
                G.add_edge(s1, s2, type='calls')

    print("Генерую тіньове IT та винятки (для A4, A6)...")
    # Додаємо аномальні прямі ролі (Shadow IT), які вибиваються із шаблонів
    shadow_users = random.sample(users, k=random.randint(20, 40))
    for user in shadow_users:
        extra_role = random.choice(roles)
        if extra_role not in user_profiles[user]:
            G.add_edge(user, extra_role, type='shadow_role')

    print("Генерую конфлікти SoD та Воркфлоу (для A7)...")
    for _ in range(25):
        r1, r2 = random.sample(roles, 2)
        G.add_edge(r1, r2, type='conflicts_with')

    for wf in workflows:
        wf_steps = random.sample(services, k=random.randint(5, 15))
        for i, step_srv in enumerate(wf_steps):
            G.add_edge(wf, step_srv, type='workflow_step', step_index=i)

    output_file = "iam_graph_full.json"
    print(f"Зберігаю граф у форматі JSON: {output_file}...")

    # 4. Експорт у Node-Link JSON
    data = nx.node_link_data(G)
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    print(
        f"Готово! Згенеровано: {num_users} юзерів, {num_roles} ролей, {num_services} сервісів. Прихованих посад: {num_implicit_jobs}.")


if __name__ == "__main__":
    generate_full_graph()