from DataStructures.Map import map_linear_probing as mp
from DataStructures.Graph import digraph as G
from DataStructures.Queue import queue as q


def bfs(graph, source):
    """
    Inicia un recorrido Breath First Seacrh (BFS) sobre el grafo a partir de un vertice inicial. 
    Crea una estructura de busqueda graph_search y posteriormente llama a la funcion bfs_vertex.
    """
    visited = {}
    edge_to = {}

    if not mp.contains(graph["vertices"], source):
        return {"visited": visited, "edge_to": edge_to, "source": source}

    queue = q.new_queue()
    q.enqueue(queue, source)
    visited[source] = True

    while not q.is_empty(queue):
        current = q.dequeue(queue)
        try:
            adj_map = G.adjacents(graph, current)  
        except Exception:
            continue  

        edges_list = mp.value_set(adj_map)
        elements = edges_list["elements"] if isinstance(edges_list, dict) else edges_list

        for edge in elements:
            if edge is None:
                continue
            neighbor = edge["to"] if isinstance(edge, dict) else edge.get("to")
            if neighbor is None:
                continue

            if neighbor not in visited:
                visited[neighbor] = True
                edge_to[neighbor] = current
                q.enqueue(queue, neighbor)

    return {"visited": visited, "edge_to": edge_to, "source": source}


def bfs_vertex(graph, source, vertex):
    """
    Función auxiliar para calcular un recorrido BFS.
    """
    if not mp.contains(graph["vertices"], source):
        return {"visited": {}, "edge_to": {}, "source": source}

    visited = {}
    edge_to = {}
    queue = q.new_queue()

    q.enqueue(queue, source)
    visited[source] = True
    found = (source == vertex)

    while not q.is_empty(queue) and not found:
        current = q.dequeue(queue)

        adj_map = G.adjacents(graph, current)
        edges_list = mp.value_set(adj_map)
        elements = edges_list["elements"] if isinstance(edges_list, dict) else edges_list

        for edge in elements:
            if edge is None:
                continue
            neighbor = edge["to"] if isinstance(edge, dict) else edge.get("to")
            if neighbor is None:
                continue

            if neighbor not in visited:
                visited[neighbor] = True
                edge_to[neighbor] = current
                q.enqueue(queue, neighbor)

                if neighbor == vertex:
                    found = True
                    break 

    return {"visited": visited, "edge_to": edge_to, "source": source}


def has_path_to(search, vertex):
    """
    Indica si existe un camino entre el vertice source y el vertice vertex 
    a partir de una estructura search.
    """
    return search["visited"].get(vertex, False)


def path_to(search, vertex):
    """
    Retorna el camino entre el vertices source y el vertice vertex 
    a partir de una estructura de busqueda search.
    """
    if not has_path_to(search, vertex):
        return None

    path = []
    current = vertex

    while current != search["source"]:
        path.append(current)
        parent = search["edge_to"].get(current)
        if parent is None:
            return None
        current = parent

    path.append(search["source"])
    path.reverse()
    return path