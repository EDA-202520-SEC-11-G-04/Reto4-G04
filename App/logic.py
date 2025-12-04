import csv
import time
import math
from datetime import datetime

# Importations des structures fournies
from DataStructures.Map import map_linear_probing as mp
from DataStructures.Graph import vertex as v
from DataStructures.Graph import digraph as graph
from DataStructures.Graph import dfs
from DataStructures.Graph import prim_structure as prim
from DataStructures.Graph import bfs
from DataStructures.Graph import dijsktra_structure as dijkstra
from DataStructures.Stack import stack as st

# --- FONCTIONS UTILITAIRES (GÉOMÉTRIE & TEMPS) ---

def haversine(lat1, lon1, lat2, lon2):
    """Calcul la distance Haversine entre deux points en km."""
    R = 6371
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

def parse_timestamp(timestamp_str):
    try:
        return datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S.%f")
    except ValueError:
        return datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")

def _load_raw_events(filename):
    """
    Étape 1 : Lit le CSV, parse les types et trie par temps.
    """
    raw_events = []
    try:
        csv.field_size_limit(2147483647)
        with open(filename, encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                if not row: continue
                try:
                    # [cite_start]Extraction et parsing [cite: 122-129]
                    w_txt = row.get('comments', '0')
                    w_dist = float(w_txt.split()[0]) if w_txt else 0.0
                    
                    event = {
                        "id": row['event-id'], 
                        "ts": parse_timestamp(row['timestamp']), 
                        "lat": float(row['location-lat']), 
                        "lon": float(row['location-long']), 
                        "tag": row['tag-local-identifier'], 
                        "w_dist": w_dist
                    }
                    raw_events.append(event)
                except ValueError:
                    continue 
    except Exception as e:
        print(f"Erreur lecture fichier: {e}")
        return []

    # Tri chronologique indispensable pour la logique de clustering
    raw_events.sort(key=lambda x: x['ts'])
    return raw_events

def _build_nodes(catalog, raw_events):
    """
    Étape 2 : Clustering des événements en Vértices.
    """
    g_dist = catalog["graph_dist"]
    g_water = catalog["graph_water"]
    event_map = catalog["event_to_node"]
    nodes_order = catalog["nodes_creation_order"] # Récupération de la liste ordonnée

    active_nodes_info = [] 
    
    for ev in raw_events:
        assigned_key = None
        
        # Nettoyer les nœuds actifs trop vieux (> 3h)
        active_nodes_info = [
            n for n in active_nodes_info 
            if (ev['ts'] - n['last_update']).total_seconds() <= 3 * 3600
        ]

        # Chercher un nœud existant compatible
        for node_info in active_nodes_info:
            dist = haversine(ev['lat'], ev['lon'], node_info['lat'], node_info['lon'])
            if dist < 3.0:
                time_diff = abs((ev['ts'] - node_info['creation_time']).total_seconds()) / 3600.0
                if time_diff < 3.0:
                    assigned_key = node_info['key']
                    
                    # Mise à jour du nœud (par référence)
                    node_info['bird_ids'].add(ev['tag'])
                    node_info['event_count'] += 1
                    node_info['sum_water'] += ev['w_dist']
                    if ev['ts'] > node_info['last_update']:
                        node_info['last_update'] = ev['ts']
                    
                    mp.put(event_map, ev['id'], assigned_key)
                    break
        
        # Créer un nouveau nœud
        if assigned_key is None:
            new_key = ev['id']
            new_info = {
                "key": new_key,
                "lat": ev['lat'], "lon": ev['lon'],
                "creation_time": ev['ts'], "last_update": ev['ts'],
                "bird_ids": {ev['tag']}, 
                "event_count": 1, "sum_water": ev['w_dist']
            }
            
            graph.insert_vertex(g_dist, new_key, new_info)
            graph.insert_vertex(g_water, new_key, new_info)
            mp.put(event_map, ev['id'], new_key)
            
            # Sauvegarder l'ordre de création
            nodes_order.append(new_key)
            
            active_nodes_info.append(new_info)
            
    return len(nodes_order)

def _build_edges(catalog, raw_events):
    """
    Étape 3 : Création des Arcs.
    """
    event_map = catalog["event_to_node"]
    g_dist = catalog["graph_dist"]
    g_water = catalog["graph_water"]
    
    #Grouper par grue
    cranes_paths = {}
    for ev in raw_events:
        cranes_paths.setdefault(ev['tag'], []).append(ev)

    edges_dist_weights = {}
    edges_water_weights = {}

    #Analyser les trajets
    for tag, path in cranes_paths.items():
        prev_node_key = None
        
        for ev in path:
            curr_node_key = mp.get(event_map, ev['id'])
            if curr_node_key is None: continue

            if prev_node_key and curr_node_key != prev_node_key:
                edge_key = (prev_node_key, curr_node_key)
                
                # Récupération des Vertex
                vertex_prev = mp.get(g_dist['vertices'], prev_node_key)
                vertex_curr = mp.get(g_dist['vertices'], curr_node_key)
                
                v_prev_info = vertex_prev['value']
                v_curr_info = vertex_curr['value']

                # Calcul Poids
                d_travel = haversine(v_prev_info['lat'], v_prev_info['lon'], v_curr_info['lat'], v_curr_info['lon'])
                avg_water = v_curr_info['sum_water'] / v_curr_info['event_count']

                edges_dist_weights.setdefault(edge_key, []).append(d_travel)
                edges_water_weights.setdefault(edge_key, []).append(avg_water)

            prev_node_key = curr_node_key

    # Ajouter les arcs
    count = 0
    for (u, v_key), weights in edges_dist_weights.items():
        graph.add_edge(g_dist, u, v_key, sum(weights) / len(weights))
        w_list = edges_water_weights[(u, v_key)]
        graph.add_edge(g_water, u, v_key, sum(w_list) / len(w_list))
        count += 1
        
    return len(cranes_paths), count


def new_logic():
    """Initialise le catalogue."""
    return {
        "graph_dist": graph.new_graph(5000),
        "graph_water": graph.new_graph(5000),
        "event_to_node": mp.new_map(25000, 0.5),
        "nodes_creation_order": [],
        "stats": {}
    }

def load_data(catalog, filename):
    print(f"Chargement de {filename}...")
    start_time = time.perf_counter()

    raw_events = _load_raw_events(filename)
    if not raw_events: return None

    total_nodes = _build_nodes(catalog, raw_events)
    total_cranes, total_edges = _build_edges(catalog, raw_events)

    catalog["stats"] = {
        "cranes": total_cranes,
        "events": len(raw_events),
        "nodes": total_nodes,
        "edges": total_edges
    }
    
    elapsed = (time.perf_counter() - start_time) * 1000
    
    print(f"Temps d'exécution (Logique): {elapsed:.2f} ms")
    
    return catalog



def get_closest_node(catalog, target_lat, target_lon):
    """
    Trouve l'ID du nœud le plus proche.
    """
    g_dist = catalog["graph_dist"]
    nodes_order = catalog["nodes_creation_order"]
    
    closest_id = None
    min_dist = float('inf')
    
    for node_id in nodes_order:
        vertex_entry = mp.get(g_dist['vertices'], node_id)
        if not vertex_entry: continue
        
        info = vertex_entry['value']
        dist = haversine(target_lat, target_lon, info['lat'], info['lon'])
        
        if dist < min_dist:
            min_dist = dist
            closest_id = node_id
            
    return closest_id, min_dist

def _build_path_details(graph_data, path_ids):
    """
    Construit les détails du chemin.
    """
    details = []
    total_dist = 0.0
    
    for i, node_id in enumerate(path_ids):
        vertex_entry = mp.get(graph_data['vertices'], node_id)
        if not vertex_entry: continue

        info = vertex_entry['value']
        dist_next = 0.0
        
        if i < len(path_ids) - 1:
            next_id = path_ids[i+1]
            next_entry = mp.get(graph_data['vertices'], next_id)
            if next_entry:
                next_info = next_entry['value']
                dist_next = haversine(info['lat'], info['lon'], next_info['lat'], next_info['lon'])
                total_dist += dist_next

        birds = list(info['bird_ids'])
        birds_fmt = str(birds[:3] + birds[-3:]) if len(birds) > 6 else str(birds)

        details.append({
            "id": node_id,
            "lat": info['lat'],
            "lon": info['lon'],
            "birds_count": info['event_count'],
            "birds_sample": birds_fmt,
            "dist_next": dist_next
        })
        
    return details, total_dist

def req_1(catalog, lat_org, lon_org, lat_dest, lon_dest, crane_id):
    """
    Exécute DFS et retourne les résultats.
    """
    if dfs is None:
        return {"error": "DFS module not loaded."}
        
    graph_obj = catalog["graph_dist"] 
    
    # Trouver les nœuds
    start_node, dist_start = get_closest_node(catalog, lat_org, lon_org)
    end_node, dist_end = get_closest_node(catalog, lat_dest, lon_dest)
    
    if not start_node or not end_node:
        return {"error": "No se encontraron nodos cercanos."}

    # Exécuter DFS

    search_result = dfs.dfs(graph_obj, start_node)
    
    #Récupérer le chemin
    path_ids = dfs.path_to(search_result, end_node)
    
    if path_ids is None:
        return {"error": f"No existe camino DFS entre {start_node} y {end_node}."}
    
    # Détails
    path_details, total_dist = _build_path_details(graph_obj, path_ids)
    
    vertex_start = mp.get(graph_obj['vertices'], start_node)
    start_has_bird = crane_id in vertex_start['value']['bird_ids']
    
    msg = f"Individuo {crane_id}: Ruta desde {start_node} hasta {end_node}"
    if start_has_bird:
        msg += " (Avistado en origen)."
    else:
        msg += " (Proyección)."

    return {
        "message": msg,
        "total_dist": total_dist,
        "total_steps": len(path_ids),
        "details": path_details
    }
    
def req_2(catalog, lat_org, lon_org, lat_dest, lon_dest, radius_km):
    """
    Detecta los movimientos biologicos considerando un radio de area 
    de interes utilizando BFS 
    
    Parametros:
        catalog: Catálogo con los grafos
        lat_org, lon_org: Coordenadas de origen
        lat_dest, lon_dest: Coordenadas de destino
        radius_km: Radio del área de interés en km
    
    Retorno:
        dict con resultados o error
    """
    if bfs is None:
        return {"error": "Módulo BFS no disponible."}
    
    graph_obj = catalog["graph_dist"]
    
    # Encontrar nodos cercanos
    start_node, dist_start = get_closest_node(catalog, lat_org, lon_org)
    end_node, dist_end = get_closest_node(catalog, lat_dest, lon_dest)
    
    if not start_node or not end_node:
        return {"error": "No se encontraron nodos cercanos a las coordenadas."}
    
    # Ejecutar BFS
    search_result = bfs.bfs(graph_obj, start_node)
    
    # Recuperar el camino completo
    path_ids = bfs.path_to(search_result, end_node)
    
    if path_ids is None:
        return {"error": f"No existe camino BFS entre {start_node} y {end_node}."}
    
    # Obtener información del nodo origen
    vertex_start = mp.get(graph_obj['vertices'], start_node)
    start_info = vertex_start['value']
    start_lat = start_info['lat']
    start_lon = start_info['lon']
    
    last_node_in_area = start_node
    
    for node_id in path_ids:
        vertex_entry = mp.get(graph_obj['vertices'], node_id)
        if not vertex_entry:
            continue
        
        node_info = vertex_entry['value']
        dist_from_origin = haversine(start_lat, start_lon, node_info['lat'], node_info['lon'])
        
        if dist_from_origin <= radius_km:
            last_node_in_area = node_id
        else:
            break
    
    # Organizar el camino
    path_details, total_dist = _build_path_details(graph_obj, path_ids)
    
    msg = f"Último nodo en área de {radius_km} km: {last_node_in_area}"
    
    return {
        "message": msg,
        "last_in_area": last_node_in_area,
        "total_dist": total_dist,
        "total_steps": len(path_ids),
        "details": path_details
    }


def req_3(catalog):
    """
    Retorna el resultado del requerimiento 3
    """
    # TODO: Modificar el requerimiento 3
    pass


def req_4(catalog, lat_org, lon_org):
    """
    Exécute Prim pour Req 4.
    CORRECTION : Gestion robuste de la profondeur des dictionnaires et unité km.
    """
    if prim is None: return {"error": "Module Prim manquant."}
    
    graph_water = catalog["graph_water"]
    
    #Identifier le départ
    start_node, _ = get_closest_node(catalog, lat_org, lon_org)
    if not start_node:
        return {"error": "No se encontró un punto de inicio cercano."}
        
    # Exécuter Prim
    mst_struct = prim.prim_mst(graph_water, start_node)
    
    # Récupérer les résultats
    marked_map = mst_struct['marked']
    keys_col = mp.key_set(marked_map)
    
    mst_nodes = []
    if isinstance(keys_col, dict) and 'elements' in keys_col:
        mst_nodes = [k for k in keys_col['elements'] if k is not None]
    else:
        mst_nodes = keys_col if keys_col else []
        
    if len(mst_nodes) <= 1:
        return {"error": "Red no viable (aislada)."}

    # Calculs Stats
    total_cost_meters = 0.0
    dist_map = mst_struct['dist_to']
    unique_birds = set()
    
    for nid in mst_nodes:
        # Cout Distance
        d_val = mp.get(dist_map, nid)
        
        # Sécurisation si d_val est encapsulé
        val = 0.0
        if isinstance(d_val, (int, float)):
            val = float(d_val)
        elif isinstance(d_val, dict) and 'value' in d_val:
            try:
                val = float(d_val['value'])
            except:
                val = 0.0
        
        # On ignore l'infini (point de départ avant calcul)
        if val != float('inf'):
            total_cost_meters += val
            
        # Oiseaux (Robustesse maximale)
        vertex_data = mp.get(graph_water['vertices'], nid)
        
        # On cherche 'bird_ids' à différents niveaux de profondeur
        found_birds = None
        
        if isinstance(vertex_data, dict):
            # Niveau 1 : Directement dans le sommet ?
            if 'bird_ids' in vertex_data:
                found_birds = vertex_data['bird_ids']
            # Niveau 2 : Dans value ?
            elif 'value' in vertex_data and isinstance(vertex_data['value'], dict):
                if 'bird_ids' in vertex_data['value']:
                    found_birds = vertex_data['value']['bird_ids']
                # Niveau 3 : Dans value['value'] ?
                elif 'value' in vertex_data['value'] and isinstance(vertex_data['value']['value'], dict):
                    if 'bird_ids' in vertex_data['value']['value']:
                        found_birds = vertex_data['value']['value']['bird_ids']

        if found_birds:
            for b in found_birds:
                unique_birds.add(b)
                
    # Conversion explicite en KM
    total_cost_km = total_cost_meters / 1000.0
    
    return {
        "message": f"Corredor (Prim) desde {start_node}",
        "total_nodes": len(mst_nodes),
        "total_individuals": len(unique_birds),
        "total_cost": total_cost_km,
        "mst_order": mst_nodes 
    }

def req_5(catalog, lat_org, lon_org, lat_dest, lon_dest, graph_type="dist"):
    """
    Encuentra el camino más corto representando la ruta migratoria más 
    eficiente entre dos punto usando Dijkstra.
    
    Parametros:
        catalog: Catálogo con los grafos
        lat_org, lon_org: Coordenadas de origen
        lat_dest, lon_dest: Coordenadas de destino
        graph_type: "dist" para distancias o "water" para fuentes hídricas
    
    Retorno:
        dict con resultados o error
    """
    if dijkstra is None:
        return {"error": "Módulo Dijkstra no disponible."}
    
    # Seleccionar el grafo
    if graph_type == "water":
        graph_obj = catalog["graph_water"]
        cost_label = "Distancia Hídrica"
    else:
        graph_obj = catalog["graph_dist"]
        cost_label = "Distancia de Desplazamiento"
    
    # Encontrar nodos cercanos
    start_node, _ = get_closest_node(catalog, lat_org, lon_org)
    end_node, _ = get_closest_node(catalog, lat_dest, lon_dest)
    
    if not start_node or not end_node:
        return {"error": "No se encontraron nodos cercanos."}
    
    # Ejecutar Dijkstra
    try:
        dijkstra_result = dijkstra.dijkstra(graph_obj, start_node)
    except Exception as e:
        return {"error": f"Error ejecutando Dijkstra: {str(e)}"}
    
    # 3. Verificar si existe camino
    if not dijkstra.has_path_to(end_node, dijkstra_result):
        return {"error": f"No existe camino entre {start_node} y {end_node}."}
    
    path_stack = dijkstra.path_to(end_node, dijkstra_result)
    
    # Convertir pila a lista
    path_ids = []
    while not st.is_empty(path_stack):
        path_ids.append(st.pop(path_stack))
    
    # Costo total
    total_cost = dijkstra.dist_to(end_node, dijkstra_result)
    
    # 6. Construir detalles
    path_details, _ = _build_path_details(graph_obj, path_ids)
    
    # Contar arcos
    num_edges = len(path_ids) - 1 if len(path_ids) > 1 else 0
    
    return {
        "message": f"Ruta óptima desde {start_node} hasta {end_node}",
        "graph_type": graph_type,
        "cost_label": cost_label,
        "total_cost": total_cost,
        "total_nodes": len(path_ids),
        "total_edges": num_edges,
        "details": path_details
    }

def req_6(catalog):
    """
    Identifica componentes aislados del nicho con DFS
    (subredes hidircas)
    
    Parametros:
        catalog: Catálogo con los grafos
    
    Retorno:
        dict con las subredes identificadas
    """
    graph_water = catalog["graph_water"]
    nodes_order = catalog["nodes_creation_order"]
    
    if not nodes_order:
        return {"error": "No hay nodos en el grafo."}
    
    # Inicio de estructuras
    component_map = {}
    component_number = 0
    
    # Recorrer todos los nodos
    for node_id in nodes_order:
        if node_id in component_map:
            continue
        component_number += 1
        
        # Ejecutar DFS
        search_result = dfs.dfs(graph_water, node_id)
        
        for visited_node in search_result['visited'].keys():
            component_map[visited_node] = component_number
    
    # Agrupar nodos
    components = {}
    for node_id, comp_num in component_map.items():
        if comp_num not in components:
            components[comp_num] = []
        components[comp_num].append(node_id)
    
    # Ordenar componentes por tamaño
    sorted_components = sorted(
        components.items(), 
        key=lambda x: len(x[1]), 
        reverse=True
    )
    
    # Calcular estadisticas para los 5 mas grandes
    top_5 = []
    
    for comp_id, node_list in sorted_components[:5]:
        min_lat = min_lon = float('inf')
        max_lat = max_lon = float('-inf')
        unique_birds = set()
        
        for node_id in node_list:
            vertex_entry = mp.get(graph_water['vertices'], node_id)
            if not vertex_entry:
                continue
            
            info = vertex_entry['value']
            
            # Actualizar límites
            min_lat = min(min_lat, info['lat'])
            max_lat = max(max_lat, info['lat'])
            min_lon = min(min_lon, info['lon'])
            max_lon = max(max_lon, info['lon'])
            
            for bird_id in info['bird_ids']:
                unique_birds.add(bird_id)
        
        # Primeros y ultimos 3
        first_3 = node_list[:3]
        last_3 = node_list[-3:] if len(node_list) > 3 else []
        
        birds_list = list(unique_birds)
        
        top_5.append({
            "component_id": comp_id,
            "total_nodes": len(node_list),
            "min_lat": min_lat,
            "max_lat": max_lat,
            "min_lon": min_lon,
            "max_lon": max_lon,
            "first_nodes": first_3,
            "last_nodes": last_3,
            "total_birds": len(unique_birds),
            "first_birds": birds_list[:3],
            "last_birds": birds_list[-3:] if len(birds_list) > 3 else []
        })
    
    return {
        "message": f"Se identificaron {len(components)} subredes hídricas",
        "total_components": len(components),
        "top_5_components": top_5
    }


# Funciones para medir tiempos de ejecucion

def get_time():
    """
    devuelve el instante tiempo de procesamiento en milisegundos
    """
    return float(time.perf_counter()*1000)


def delta_time(start, end):
    """
    devuelve la diferencia entre tiempos de procesamiento muestreados
    """
    elapsed = float(end - start)
    return elapsed
