import json
import networkx as nx
from collections import defaultdict

print("Завантажую граф з JSON...")
with open("iam_graph_full.json", "r", encoding="utf-8") as f:
    data = json.load(f)
    G = nx.node_link_graph(data)

print("Аудит A2: Шукаємо блоки користувачів за набором сервісів...")
service_clusters = defaultdict(list)

# Проходимо по всіх вузлах
for node, attr in G.nodes(data=True):
    if attr.get('type') == 'User':
        user_services = set()  

        # 1. Шукаємо ролі користувача
        for u, role, edge_data in G.edges(node, data=True):
            if edge_data.get('type') == 'assigned_to':

                # 2. Від кожної ролі шукаємо дозволені сервіси
                for r, srv, grant_data in G.edges(role, data=True):
                    if grant_data.get('type') == 'grant':
                        user_services.add(srv)

        # Якщо юзер має хоч якісь сервіси, пакуємо їх і групуємо
        if user_services:
            service_signature = tuple(sorted(user_services))
            service_clusters[service_signature].append(node)

# Рахуємо score (кількість користувачів * кількість сервісів)
winning_score = 0
winning_users = 0
winning_services_count = 0
winning_service_ids = []

for service_signature, users in service_clusters.items():
    user_count = len(users)
    service_count = len(service_signature)
    score = user_count * service_count

    if score > winning_score:
        winning_score = score
        winning_users = user_count
        winning_services_count = service_count
        winning_service_ids = list(service_signature)

print(f"\n--- РЕЗУЛЬТАТИ A2 ---")
print(f"Кількість користувачів (User count): {winning_users}")
print(f"Кількість сервісів (Service count): {winning_services_count}")
print(f"Оцінка блоку (Score): {winning_score}")
print(f"ID сервісів (Service IDs): {', '.join(winning_service_ids)}")
