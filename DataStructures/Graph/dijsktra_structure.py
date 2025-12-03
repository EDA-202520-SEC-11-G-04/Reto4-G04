from DataStructures.Graph import dijsktra_structure as dijsktra_st
from DataStructures.Map import map_linear_probing as map
from DataStructures.Queue import priority_queue as pq
from DataStructures.Stack import stack as st
from DataStructures.List import array_list as lt
from DataStructures.Graph import digraph as G
from DataStructures.Graph import edge as E

def new_dijsktra_structure(source, g_order):
    """

    Crea una estructura de busqueda usada en el algoritmo **dijsktra**.

    Se crea una estructura de busqueda con los siguientes atributos:

    - **source**: Vertice de origen. Se inicializa en ``source``
    - **visited**: Mapa con los vertices visitados. Se inicializa en ``None``
    - **pq**: Cola indexada con los vertices visitados. Se inicializa en ``None``

    :returns: Estructura de busqueda
    :rtype: dijsktra_search
    """
    structure = {
        "source": source,
        "visited": map.new_map(
            g_order, 0.5),
        "pq": pq.new_heap()}
    return structure

def dijkstra(my_graph, source):
    """
    Implementa el algoritmo de Dijkstra para encontrar los caminos más cortos
    desde un vértice origen a todos los demás vértices del grafo.
    """
    if not G.contains_vertex(my_graph, source):
        raise Exception("El vertice origen no existe")
    
    # Crear la estructura de búsqueda
    g_order = G.order(my_graph)
    aux_structure = dijsktra_st.new_dijsktra_structure(source, g_order)
    
    # Inicializar todos los vértices
    vertices_list = G.vertices(my_graph)
    for i in range(lt.size(vertices_list)):
        key_v = lt.get_element(vertices_list, i)
        
        vertex_info = {
            "marked": False,
            "edge_from": None,
            "dist_to": float('inf')
        }
        
        map.put(aux_structure["visited"], key_v, vertex_info)
    
    # Configurar el vértice origen
    source_info = map.get(aux_structure["visited"], source)
    source_info["value"]["dist_to"] = 0
    source_info["value"]["marked"] = True
    
    # Agregar el vértice origen a la cola de prioridad
    pq.insert(aux_structure["pq"], source, 0)
    
    # Procesar la cola de prioridad
    while not pq.is_empty(aux_structure["pq"]):
        current = pq.del_min(aux_structure["pq"])
        current_key = current
        
        current_info = map.get(aux_structure["visited"], current_key)
        current_dist = current_info["value"]["dist_to"]
        
        current_info["value"]["marked"] = True
        
        adjacents_list = G.adjacents(my_graph, current_key)
        for i in range(lt.size(adjacents_list)):
            adj_key = lt.get_element(adjacents_list, i)
            
            edge = G.get_edge(my_graph, current_key, adj_key)
            edge_weight = E.weight(edge)
            
            adj_info = map.get(aux_structure["visited"], adj_key)
            
            if current_dist + edge_weight < adj_info["value"]["dist_to"]:
                adj_info["value"]["dist_to"] = current_dist + edge_weight
                adj_info["value"]["edge_from"] = current_key
                
                if map.contains(aux_structure["pq"]["qpmap"], adj_key):
                    pq.decrease_key(aux_structure["pq"], adj_key, adj_info["value"]["dist_to"])
                else:
                    pq.insert(aux_structure["pq"], adj_key, adj_info["value"]["dist_to"])
    
    return aux_structure


def dist_to(key_v, aux_structure):
    """
    Retorna la distancia mínima desde el vértice origen hasta el vértice key_v.
    """
    # Verificar que el vértice existe en la estructura
    if not map.contains(aux_structure["visited"], key_v):
        raise Exception("El vertice no existe")
    
    # Obtener y retornar la distancia
    vertex_info = map.get(aux_structure["visited"], key_v)
    return vertex_info["value"]["dist_to"]


def has_path_to(key_v, aux_structure):
    """
    Indica si existe un camino desde el vértice origen hasta el vértice key
    """
    # Verificar que el vértice existe
    if not map.contains(aux_structure["visited"], key_v):
        raise Exception("El vertice no existe")
    
    # Obtener la información del vértice
    vertex_info = map.get(aux_structure["visited"], key_v)
    
    # Existe camino si la distancia no es infinita
    return vertex_info["value"]["dist_to"] != float('inf')


def path_to(key_v, aux_structure):
    """
    Retorna el camino de menor distancia desde el vértice origen hasta key_v
    """
    # Verificar que existe un camino
    if not has_path_to(key_v, aux_structure):
        return None
    
    # Crear la pila para el camino
    path = st.new_stack()
    
    # Reconstruir el camino desde key_v hasta source
    current = key_v
    while current is not None:
        st.push(path, current)
        
        # Obtener el predecesor
        vertex_info = map.get(aux_structure["visited"], current)
        current = vertex_info["value"]["edge_from"]
    
    return path

