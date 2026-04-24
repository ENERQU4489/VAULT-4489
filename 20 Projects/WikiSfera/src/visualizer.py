import sqlite3
import json
import networkx as nx
import os

DB_PATH = "20 Projects/WikiSfera/data/wiki_graph.db"
OUTPUT_JSON = "20 Projects/WikiSfera/output/map_data.json"
TOP_N = 10000  # Liczba punktów na mapie (10k to złoty środek między jakością a szybkością)

def get_top_subgraph():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    print(f"📊 Picking top {TOP_N} articles by degree...")
    # Wybieramy strony z największą liczbą linków przychodzących
    cursor.execute("""
        SELECT to_id, COUNT(*) as degree 
        FROM links 
        GROUP BY to_id 
        ORDER BY degree DESC 
        LIMIT ?
    """, (TOP_N,))
    
    top_nodes = {row[0] for row in cursor.fetchall()}
    
    print("🆔 Fetching titles...")
    placeholders = ','.join(['?'] * len(top_nodes))
    cursor.execute(f"SELECT id, title FROM pages WHERE id IN ({placeholders})", list(top_nodes))
    id_to_title = {row[0]: row[1] for row in cursor.fetchall()}
    
    print("🔗 Fetching connections between top articles...")
    # Tylko linki, gdzie oba końce są w naszym TOP_N
    cursor.execute(f"""
        SELECT from_id, to_id 
        FROM links 
        WHERE from_id IN ({placeholders}) AND to_id IN ({placeholders})
    """, list(top_nodes) + list(top_nodes))
    
    edges = cursor.fetchall()
    conn.close()
    
    return id_to_title, edges

def generate_layout(id_to_title, edges):
    print("🧠 Preparing initial positions...")
    import random
    import math
    
    nodes_data = []
    # Rozmieszczamy punkty w dużym kole, żeby fizyka miała miejsce na "rozprężenie"
    for node_id in id_to_title.keys():
        angle = random.random() * 2 * math.pi
        radius = 500 + random.random() * 500
        nodes_data.append({
            "id": str(node_id),
            "label": id_to_title.get(node_id, "Unknown"),
            "x": math.cos(angle) * radius,
            "y": math.sin(angle) * radius,
            "size": 1, # Rozmiar policzymy niżej
            "degree": 0
        })

    # Liczymy stopnie (degree) dla rozmiarów
    node_degrees = {str(n): 0 for n in id_to_title.keys()}
    edges_data = []
    for i, (u, v) in enumerate(edges):
        u_s, v_s = str(u), str(v)
        if u_s in node_degrees and v_s in node_degrees:
            node_degrees[u_s] += 1
            node_degrees[v_s] += 1
            if i < 25000: # Redukcja krawędzi dla przejrzystości
                edges_data.append({
                    "id": f"e{i}",
                    "source": u_s,
                    "target": v_s
                })

    # Aktualizacja rozmiarów (skalowanie logarytmiczne)
    for n in nodes_data:
        deg = node_degrees[n["id"]]
        n["size"] = math.log(deg + 1.1) * 3 + 1
        n["degree"] = deg
        
    print(f"💾 Saving {len(nodes_data)} nodes and {len(edges_data)} edges...")
    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump({"nodes": nodes_data, "edges": edges_data}, f)

def serve_map():
    import webbrowser
    import http.server
    import socketserver
    import threading

    PORT = 8000
    DIRECTORY = "20 Projects/WikiSfera/output"

    class Handler(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=DIRECTORY, **kwargs)

    def start_server():
        with socketserver.TCPServer(("", PORT), Handler) as httpd:
            print(f"🌍 Map server running at http://localhost:{PORT}")
            httpd.serve_forever()

    # Odpalamy serwer w osobnym wątku
    thread = threading.Thread(target=start_server, daemon=True)
    thread.start()

    # Otwieramy przeglądarkę
    print("🚀 Opening map in browser...")
    webbrowser.open(f"http://localhost:{PORT}/map.html")
    
    # Dajemy użytkownikowi chwilę na nacieszenie oka
    input("\nPress ENTER to stop the server and exit...")

if __name__ == "__main__":
    id_to_title, edges = get_top_subgraph()
    generate_layout(id_to_title, edges)
    print(f"✅ Map data ready in {OUTPUT_JSON}")
    serve_map()
