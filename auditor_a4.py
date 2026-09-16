import networkx as nx
import json


def analyze_a4_exceptions(file_path="iam_graph_full.json"):
    print(f"Завантажую граф з {file_path}...")
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        G = nx.node_link_graph(data)
    except Exception as e:
        print(f"Помилка завантаження файлу: {e}")
        return

    print("Аудит A4: Топологічний пошук прямих доступів (User -> Service)...")

    exceptions = []

    # Проходимо по всіх ребрах графа
    for u, v, d in G.edges(data=True):
        # Отримуємо типи вузлів на обох кінцях зв'язку
        source_type = G.nodes[u].get('type')
        target_type = G.nodes[v].get('type')

        # Топологічна перевірка: чи є це прямий зв'язок між людиною та сервісом?
        if source_type == 'User' and target_type == 'Service':
            exceptions.append((u, v))

    print(f"\n--- РЕЗУЛЬТАТ A4 ---")
    print(f"Знайдено 'сміттєвих' прямих доступів: {len(exceptions)}")
    if exceptions:
        print("Приклади порушень (User -> Service):")
        # Виводимо перші 15 для демонстрації
        for user_id, srv_id in exceptions[:15]:
            print(f"  {user_id} має прямий доступ до {srv_id}")
        if len(exceptions) > 15:
            print("  ... і так далі.")


if __name__ == "__main__":
    # analyze_a4_exceptions("iam_graph_full.json")
    analyze_a4_exceptions("iam_graph_small.json")
