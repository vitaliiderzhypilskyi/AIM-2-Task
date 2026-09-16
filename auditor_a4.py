import networkx as nx
import json


def analyze_a4_exceptions(file_path="iam_graph_small.json"):
    print(f"Завантажую граф з {file_path}...")
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        G = nx.node_link_graph(data)
    except Exception as e:
        print(f"Помилка завантаження файлу: {e}")
        return

    print("Аудит A4: Пошук 'винятків' у визначеннях ролей (Role -> Service)...")

    # Збираємо всі ролі та сервіси, до яких вони дають доступ
    role_grants = {}
    service_roles = {}
    for u, v, d in G.edges(data=True):
        if d.get('type') == 'grant':
            role_grants.setdefault(u, set()).add(v)
            service_roles.setdefault(v, set()).add(u)

    exceptions = []

    # Аналізуємо кожен grant
    for role, services in role_grants.items():
        # Якщо в ролі всього 1-2 сервіси, важко статистично назвати їх винятками
        if len(services) <= 2:
            continue

        for srv in services:
            # Шукаємо "підтримку" (support) для цього доступу
            shared_support = 0
            other_services = services - {srv}

            for other_srv in other_services:
                # Перевіряємо, чи перетинаються інші ролі, які дають доступ до srv та other_srv одночасно
                if len(service_roles[srv].intersection(service_roles[other_srv])) > 1:
                    shared_support += 1

            # Якщо цей сервіс НІКОЛИ не видається разом з іншими сервісами цієї ролі
            # Значить, він пришитий сюди штучно, і жодна Job Function його не пояснює
            if shared_support == 0:
                exceptions.append((role, srv))

    print(f"\n--- РЕЗУЛЬТАТ A4 ---")
    print(f"Знайдено 'сміттєвих' дозволів (Role -> Service): {len(exceptions)}")
    if exceptions:
        print("Приклади винятків:")
        for r, s in exceptions[:15]:
            print(f"  {r} має аномальний доступ до {s}")


if __name__ == "__main__":
    analyze_a4_exceptions("iam_graph_small.json")
    # analyze_a4_exceptions("iam_graph_full.json")
