from DataStructures.Map import map_linear_probing as mp
from DataStructures.Graph import vertex as v  
from DataStructures.Graph import edge as e

DEFAULT_LOAD_FACTOR = 0.5
DEFAULT_PRIME = 109345121


def new_graph(order):
    graph = {
        "vertices": mp.new_map(order, DEFAULT_LOAD_FACTOR, DEFAULT_PRIME),
        "num_edges": 0
    }
    return graph


def insert_vertex(my_graph, key_u, info_u):

    adj_map = mp.new_map(3, DEFAULT_LOAD_FACTOR, DEFAULT_PRIME)

    vertex = {
        "key": key_u,
        "value": info_u,
        "adjacents": adj_map
    }

    mp.put(my_graph["vertices"], key_u, vertex)

    return my_graph


def add_edge(graph, key_u, key_v, weight=1.0):

    if not mp.contains(graph["vertices"], key_u):
        raise Exception("El vertice u no existe")

    if not mp.contains(graph["vertices"], key_v):
        raise Exception("El vertice v no existe")

    vertex_u = mp.get(graph["vertices"], key_u)  # <-- direct

    existing_edge = v.get_edge(vertex_u, key_v)

    if existing_edge is None:
        new_edge = e.new_edge(key_v, weight)
        v.add_adjacent(vertex_u, key_v, new_edge)
        graph["num_edges"] += 1
    else:
        existing_edge["weight"] = weight

    return graph


def contains_vertex(graph, key):
    """
    Verifica si el vértice con key existe en el grafo.
    """
    return mp.contains(graph['vertices'], key)

def order(graph):
    """
    Retorna el orden (número de vértices) del grafo.
    """
    return mp.size(graph['vertices'])

def size(graph):
    return graph["num_edges"]


def degree(graph, key_u):
    if not mp.contains(graph["vertices"], key_u):
        raise Exception("El vertice no existe")

    vertex_u = mp.get(graph["vertices"], key_u)
    adj = v.get_adjacents(vertex_u)
    return mp.size(adj)

def adjacents(graph, key_u):
    """
    Retorna el mapa de arcos adyacentes al vértice key_u.
    """
    if not mp.contains(graph["vertices"], key_u):
        raise Exception("El vertice no existe")
    vertex_u = mp.get(graph["vertices"], key_u)
    return v.get_adjacents(vertex_u)


# ------------------------------------------------
def vertices(graph):
    """
    Retorna la lista (array_list) con las llaves de todos los vertices.
    """
    return mp.key_set(graph["vertices"])


# ------------------------------------------------
def edges_vertex(graph, key_u):
    """
    Retorna la lista (array_list) con los arcos salientes del vertice key_u.
    """
    if not mp.contains(graph["vertices"], key_u):
        raise Exception("El vertice no existe")
    adj = adjacents(graph, key_u)
    return mp.value_set(adj)


# ------------------------------------------------
def get_vertex(graph, key):
    """
    Retorna el vertice (dict) almacenado en graph['vertices'] o None.
    """
    return mp.get(graph["vertices"], key)


# ------------------------------------------------
def update_vertex_info(graph, key, new_info):
    """
    Actualiza la información asociada al vértice (campo 'value').
    """
    if not mp.contains(graph["vertices"], key):
        raise Exception("El vertice no existe")
    vertex = mp.get(graph["vertices"], key)
    v.set_value(vertex, new_info)
    mp.put(graph["vertices"], key, vertex)
    return graph

def get_vertex_information(my_graph, key_u):
    """
    Retorna la informacion (value) asociada al vertice con llave key_u
    Si el vertice no existe, se lanza una excepcion.
    """
    # Verificamos si el vértice existe en el mapa de vértices del grafo
    if not mp.contains(my_graph['vertices'], key_u):
        raise Exception("El vertice no existe")
    
    vertex_entry = mp.get(my_graph['vertices'], key_u)
    vertex = vertex_entry['value']
    
    return v.get_value(vertex)