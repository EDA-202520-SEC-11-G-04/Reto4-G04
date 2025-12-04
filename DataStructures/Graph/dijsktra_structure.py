from DataStructures.Graph import dijsktra_structure as dijsktra_st
from DataStructures.Map import map_linear_probing as mp
from DataStructures.Priority_queue import priority_queue as pq
from DataStructures.Stack import stack as st
from DataStructures.List import array_list as lt
from DataStructures.Graph import digraph as G
from DataStructures.Graph import edge as E
import heapq

def dijkstra(graph, source):
    """
    Implementa Dijkstra para encontrar caminos más cortos desde source.
    
    """
    # Verificar que el vértice origen existe
    if not mp.contains(graph['vertices'], source):
        raise Exception(f"El vértice origen {source} no existe")
    
    # Inicializar estructuras
    dist_to = {source: 0.0}
    edge_from = {}
    visited = {}
    
    pq = [(0.0, source)]
    
    while pq:
        current_dist, current = heapq.heappop(pq)
        
        if current in visited:
            continue
        
        visited[current] = True
        
        # Obtener vecinos
        try:
            adj_map = G.adjacents(graph, current)
        except:
            continue
        
        # Obtener aristas
        edges_list = mp.value_set(adj_map)
        elements = edges_list.get("elements", []) if isinstance(edges_list, dict) else edges_list
        
        if not elements:
            continue
        
        # Procesar vacinos
        for edge in elements:
            if edge is None:
                continue
            
            neighbor = edge.get("to") if isinstance(edge, dict) else None
            if neighbor is None:
                continue
            
            weight = edge.get("weight", 1.0) if isinstance(edge, dict) else 1.0
            if isinstance(weight, dict):
                weight = weight.get("value", 1.0)
            weight = float(weight)
            
            new_dist = current_dist + weight
            
            if neighbor not in dist_to or new_dist < dist_to[neighbor]:
                dist_to[neighbor] = new_dist
                edge_from[neighbor] = current
                heapq.heappush(pq, (new_dist, neighbor))
    
    return {
        "source": source,
        "dist_to": dist_to,
        "edge_from": edge_from,
        "visited": visited
    }


def has_path_to(vertex, search):
    """
    Indica si existe un camino desde source hasta vertex.
    """
    return vertex in search["dist_to"] and search["dist_to"][vertex] != float('inf')


def dist_to(vertex, search):
    """
    Retorna la distancia mínima desde source hasta vertex.
    """
    if vertex not in search["dist_to"]:
        return float('inf')
    return search["dist_to"][vertex]


def path_to(vertex, search):
    """
    Retorna el camino desde source hasta vertex como una lista.
    """
    if not has_path_to(vertex, search):
        return None
    
    path = []
    current = vertex
    
    # Reconstruir camino desde vertex hasta source
    while current is not None:
        path.append(current)
        current = search["edge_from"].get(current)
    
    # Invertir
    path.reverse()
    
    return path