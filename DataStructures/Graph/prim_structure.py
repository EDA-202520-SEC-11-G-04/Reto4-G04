from DataStructures.Map import map_linear_probing as map
from DataStructures.Priority_queue import priority_queue as pq
from DataStructures.Queue import queue as q

def new_prim_structure(source, g_order):
    structure = {
        "source": source,
        "edge_from": map.new_map(g_order, 0.5),
        "dist_to": map.new_map(g_order, 0.5),
        "marked": map.new_map(g_order, 0.5),
        "pq":  pq.new_heap(),
    }
    return structure

def _get_value_recursively(data):
    """
    Fonction helper robuste : Cherche un nombre (int/float) récursivement 
    si la donnée est emballée dans des dictionnaires (Entry, Value, Weight...).
    """
    # Cas de base : c'est un nombre
    if isinstance(data, (int, float)):
        return float(data)
    
    # Cas récursif : c'est un dictionnaire
    if isinstance(data, dict):
        # On cherche les clés probables par ordre de priorité
        if 'weight' in data:
            return _get_value_recursively(data['weight'])
        if 'value' in data:
            return _get_value_recursively(data['value'])
        if 'info' in data:
            return _get_value_recursively(data['info'])
            
    # Si on ne trouve rien ou type inconnu -> Infini
    return float('inf')

def _extract_vertex_data(map_entry):
    """
    Extrait la structure Vertex (qui contient 'adjacents') depuis une Entry de Map.
    """
    if not isinstance(map_entry, dict): return None
    
    # Si c'est directement le vertex
    if 'adjacents' in map_entry:
        return map_entry
    
    # Si c'est une Entry {key, value=Vertex}
    if 'value' in map_entry:
        val = map_entry['value']
        if isinstance(val, dict) and 'adjacents' in val:
            return val
            
    return None

def prim_mst(graph, source):
    g_size = map.size(graph['vertices'])
    mst = new_prim_structure(source, g_size)
    
    map.put(mst['dist_to'], source, 0.0)
    pq.insert(mst['pq'], 0.0, source)
    
    while not pq.is_empty(mst['pq']):
        u = pq.remove(mst['pq'])
        
        if u is None or map.contains(mst['marked'], u):
            continue
            
        map.put(mst['marked'], u, True)
        _scan(graph, mst, u)
        
    return mst

def _scan(graph, mst, u):
    # 1. Récupérer l'entrée brute
    raw_u = map.get(graph['vertices'], u)
    if not raw_u: return
    
    # 2. Extraire la structure Vertex (pour avoir adjacents)
    vertex_u = _extract_vertex_data(raw_u)
    if not vertex_u: return
    
    adj_map = vertex_u.get('adjacents')
    if not adj_map: return
    
    # 3. Parcourir voisins
    keys_col = map.key_set(adj_map)
    if isinstance(keys_col, dict) and 'elements' in keys_col:
        neighbors_ids = [k for k in keys_col['elements'] if k is not None]
    else:
        neighbors_ids = keys_col if keys_col else []

    for v in neighbors_ids:
        if map.contains(mst['marked'], v):
            continue
            
        # 4. Récupérer l'arc
        edge_data = map.get(adj_map, v)
        if not edge_data: continue
        
        # --- UTILISATION DE LA FONCTION ROBUSTE ---
        weight = _get_value_recursively(edge_data)
        
        # 5. Distance actuelle
        current_dist = float('inf')
        if map.contains(mst['dist_to'], v):
            raw_dist = map.get(mst['dist_to'], v)
            # dist_to peut aussi contenir des Entries, on utilise la même fonction
            current_dist = _get_value_recursively(raw_dist)
            
        # 6. Relaxation
        if weight < current_dist:
            map.put(mst['dist_to'], v, weight)
            map.put(mst['edge_from'], v, u)
            pq.insert(mst['pq'], weight, v)