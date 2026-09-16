import networkx as nx
import json


def analyze_a1_clique(file_path="iam_graph_full.json"):
    print("Завантажую граф з JSON...")
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        G = nx.node_link_graph(data)
    except Exception as e:
        print(f"Помилка завантаження файлу: {e}")
        return

    print("Аналізую взаємодію між сервісами (шукаю двосторонні виклики)...")

    # Створюємо неорієнтований граф для ідеальних двосторонніх зв'язків
    mutual_G = nx.Graph()

    # Швидкий пошук: збираємо всі орієнтовані виклики у множину
    calls = {(u, v) for u, v, d in G.edges(data=True) if d.get('type') == 'calls'}

    # Залишаємо лише ті, де є виклик туди-назад
    for u, v in calls:
        if (v, u) in calls and u != v:
            mutual_G.add_edge(u, v)

    print("Застосовую алгоритм Брона-Кербоша для пошуку максимальної кліки...")
    cliques = list(nx.find_cliques(mutual_G))

    if not cliques:
        print("Взаємних груп сервісів не знайдено.")
    else:
        largest_clique = max(cliques, key=len)
        print(f"\n--- РЕЗУЛЬТАТ A1 ---")
        print(f"Розмір найбільшої групи (кліки): {len(largest_clique)}")
        print(f"ID сервісів: {', '.join(sorted(largest_clique))}")


if __name__ == "__main__":
    analyze_a1_clique("iam_graph_full.json")
    # analyze_a1_clique("iam_graph_small.json")
