from DataStructures.Map import map_linear_probing as mp
from DataStructures.Graph import digraph as G

def dfs(graph, source):
    """
    Ejecuta DFS desde 'source' y retorna la estructura de búsqueda.
    {
      "visited": dict(vertice -> True),
      "edge_to": dict(v -> parent),
      "source": source
    }
    """
    visited = {}
    edge_to = {}
    # si source no existe en el grafo, devolver estructura vacia con source
    if not mp.contains(graph["vertices"], source):
        return {"visited": visited, "edge_to": edge_to, "source": source}
    _dfs_vertex(graph, source, visited, edge_to)
    return {"visited": visited, "edge_to": edge_to, "source": source}


def _dfs_vertex(graph, vtx, visited, edge_to):
    visited[vtx] = True
    try:
        adj_map = G.adjacents(graph, vtx)
    except Exception:
        return
    edges_arr = mp.value_set(adj_map)
    # value_set retorna array_list-like
    elements = edges_arr["elements"] if isinstance(edges_arr, dict) and "elements" in edges_arr else edges_arr
    if elements is None:
        return
    for edge in elements:
        if edge is None:
            continue
        to = edge.get("to") if isinstance(edge, dict) else edge["to"]
        if to is None:
            continue
        if to not in visited:
            edge_to[to] = vtx
            _dfs_vertex(graph, to, visited, edge_to)


def has_path_to(search, v):
    return search["visited"].get(v, False)


def path_to(search, v):
    if not has_path_to(search, v):
        return None
    path = []
    cur = v
    while cur != search["source"]:
        path.append(cur)
        cur = search["edge_to"].get(cur)
        if cur is None:
            return None
    path.append(search["source"])
    path.reverse()
    return path
