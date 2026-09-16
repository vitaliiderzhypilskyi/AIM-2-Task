import networkx as nx
import json
import os


def convert_json_to_graphml(input_file, output_file):
    if not os.path.exists(input_file):
        print(f"[-] Файл {input_file} не знайдено! Спочатку запустіть генератор.")
        return

    print(f"[*] Читаю {input_file}...")
    with open(input_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    G = nx.node_link_graph(data)

    print(f"[*] Очищаю атрибути для сумісності з GraphML...")
    # Проходимося по всіх вузлах
    for node, attrs in G.nodes(data=True):
        # Встановлюємо ім'я вузла як його label для Gephi
        attrs['label'] = str(node)

        # Перетворюємо всі складні типи даних на рядки
        for key, val in list(attrs.items()):
            if isinstance(val, (list, dict, set)):
                attrs[key] = str(val)
            elif val is None:
                attrs[key] = ""

    # Проходимося по всіх зв'язках
    for u, v, attrs in G.edges(data=True):
        for key, val in list(attrs.items()):
            if isinstance(val, (list, dict, set)):
                attrs[key] = str(val)
            elif val is None:
                attrs[key] = ""

    print(f"[*] Зберігаю як {output_file}...")
    nx.write_graphml(G, output_file)
    print(f"[+] Готово! Можна відкривати {output_file} у Gephi.\n")


if __name__ == "__main__":
    # Конвертуємо малий граф для візуального аналізу (скріншоти для звіту)
    convert_json_to_graphml("iam_graph_small.json", "iam_graph_small.graphml")

    # Конвертуємо великий граф (опціонально, обережно при відкритті в Gephi!)
    convert_json_to_graphml("iam_graph_full.json", "iam_graph_full.graphml")
