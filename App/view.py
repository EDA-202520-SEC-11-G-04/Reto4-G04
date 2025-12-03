import sys
import App.logic as logic
from tabulate import tabulate
from DataStructures.Map import map_linear_probing as mp


def new_logic():
    """
        Se crea una instancia del controlador
    """
    #TODO: Llamar la función de la lógica donde se crean las estructuras de datos
    return logic.new_logic()

def print_menu():
    print("Bienvenido")
    print("0- Cargar información")
    print("1- Ejecutar Requerimiento 1")
    print("2- Ejecutar Requerimiento 2")
    print("3- Ejecutar Requerimiento 3")
    print("4- Ejecutar Requerimiento 4")
    print("5- Ejecutar Requerimiento 5")
    print("6- Ejecutar Requerimiento 6")
    print("7- Salir")

def _format_node_row(graph, key):
    """
    Prépare une ligne pour le tableau tabulate (pour l'affichage en liste).
    """
    # 1. Récupérer l'entrée dans la Map des sommets
    vertex_entry = mp.get(graph['vertices'], key)
    if not vertex_entry:
        return ["Erreur", "", "", "", "", ""]
    
    # 2. Récupérer le payload (dictionnaire d'info)
    info = vertex_entry['value']
    
    # 3. Formatage
    pos_str = f"({info['lat']:.5f}, {info['lon']:.5f})"
    date_str = info['creation_time'].strftime("%Y-%m-%d %H:%M:%S")
    
    # Gestion des listes de tags (tronquer si trop long)
    tags_list = list(info['bird_ids'])
    tags_str = str(tags_list)
    if len(tags_str) > 20:
        tags_str = f"{str(tags_list[:1])[:-1]}...]"
    
    avg_water = info['sum_water'] / info['event_count']
    
    # Retourner la liste ordonnée des colonnes
    return [
        info['key'],
        pos_str,
        date_str,
        tags_str,
        info['event_count'],
        f"{avg_water:.4f}"
    ]

# ==============================================================================
# FONCTIONS D'AFFICHAGE PRINCIPALES
# ==============================================================================

def print_load_report(catalog):
    """
    Affiche le rapport complet de chargement (Stats + Tableaux des nœuds).
    Correspond aux Figures 1 et 2 du PDF.
    """
    if not catalog or 'stats' not in catalog:
        print("Erreur : Catalogue vide ou invalide.")
        return

    stats = catalog['stats']
    nodes_order = catalog['nodes_creation_order']
    # On utilise graph_dist pour lire les infos (ce sont les mêmes nœuds que graph_water)
    graph = catalog['graph_dist']

    # --- PARTIE 1 : STATISTIQUES ---
    print("\n" + "="*60)
    print("CARGA DE DATOS")
    print("="*60)
    
    stats_data = [
        ["Total de grullas reconocidas", stats['cranes']],
        ["Total de eventos cargados", stats['events']],
        ["Total de nodos del grafo", stats['nodes']],
        ["Total de arcos en el grafo", stats['edges']]
    ]
    print(tabulate(stats_data, tablefmt="plain"))
    print("="*60)

    # --- PARTIE 2 : TABLEAUX DES NOEUDS ---
    print("\nDETALLE DE NODOS (VERTICES)")
    
    headers = ["ID", "Posición (lat, lon)", "Fecha Creación", "Grullas", "Eventos", "Dist. Agua (km)"]
    
    # 5 Premiers Nœuds
    print("\n--- Primeros 5 Nodos ---")
    if nodes_order:
        first_rows = [_format_node_row(graph, key) for key in nodes_order[:5]]
        print(tabulate(first_rows, headers=headers, tablefmt="fancy_grid"))
    else:
        print("Aucun nœud.")

    # 5 Derniers Nœuds
    if len(nodes_order) > 5:
        print("\n--- Últimos 5 Nodos ---")
        last_rows = [_format_node_row(graph, key) for key in nodes_order[-5:]]
        print(tabulate(last_rows, headers=headers, tablefmt="fancy_grid"))
    
    print("\n" + "="*60)


def print_data(control, node_id):
    """
    Imprime les détails d'un nœud spécifique donné par son ID.
    Utile pour afficher un résultat de recherche précis.
    """
    if not control or 'graph_dist' not in control:
        print("Catalogue vide.")
        return
    
    graph = control['graph_dist']
    
    # Recherche du nœud dans la Map
    entry = mp.get(graph['vertices'], node_id)
    
    if not entry:
        print(f"Erreur : Le nœud avec l'ID '{node_id}' n'existe pas.")
        return
    
    # Extraction des données
    info = entry['value']
    avg_water = info['sum_water'] / info['event_count']
    
    # Préparation des données pour un tableau vertical
    data = [
        ["ID Unique", info['key']],
        ["Latitud", f"{info['lat']:.6f}"],
        ["Longitud", f"{info['lon']:.6f}"],
        ["Fecha Creación", info['creation_time'].strftime("%Y-%m-%d %H:%M:%S")],
        ["Última Actualización", info['last_update'].strftime("%Y-%m-%d %H:%M:%S")],
        ["Grullas (Tags)", str(list(info['bird_ids']))],
        ["Total Eventos Agrupados", info['event_count']],
        ["Distancia Promedio Agua", f"{avg_water:.4f} km"]
    ]
    
    print("\n--- Detalles del Nodo ---")
    print(tabulate(data, headers=["Atributo", "Valor"], tablefmt="fancy_grid"))

# ==============================================================================
# MENU / CHARGEMENT
# ==============================================================================

def load_data(control):
    """
    Fonction de la vue qui appelle la logique et affiche le résultat.
    """
    filename = input("Nombre del archivo a cargar (ej: Data/1000_cranes_mongolia_small.csv): ")
    try:
        control = logic.load_data(control, filename)
        
        # Si le chargement est réussi, on affiche le rapport
        if control:
            print_load_report(control)
        else:
            print("Erreur lors du chargement des données.")
            
    except Exception as e:
        print(f"Une erreur est survenue : {e}")
        # Optionnel: afficher la trace complète pour le débogage
        # import traceback
        # traceback.print_exc()
        
    return control

def _format_req1_row(detail_dict):
    """
    Helper pour req_1 : Formate une ligne spécifique au chemin (avec distance au suivant).
    """
    # Gestion propre de l'affichage de la distance
    dist_val = detail_dict['dist_next']
    if isinstance(dist_val, (int, float)) and dist_val > 0:
        dist_s = f"{dist_val:.4f}"
    else:
        dist_s = "-" # Pour le dernier nœud

    return [
        detail_dict['id'],
        f"({detail_dict['lat']:.4f}, {detail_dict['lon']:.4f})",
        detail_dict['birds_count'],
        detail_dict['birds_sample'],
        dist_s
    ]

def print_req_1(control):
    """
    Vue pour le Requis 1 : Chemin DFS d'un individu.
    """
    print("\n" + "="*60)
    print("REQ. 1: Detectar camino de un individuo (DFS)")
    print("="*60)
    
    if control is None or 'graph_dist' not in control:
        print("Error: Debe cargar los datos primero.")
        return

    try:
        # 1. Inputs Utilisateur
        print("Ingrese coordenadas (Deje vacío para usar valores por defecto):")
        
        l_org = input("Latitud Origen (ej: 48.0): ")
        lat_org = float(l_org) if l_org else 48.47
        
        l_lon = input("Longitud Origen (ej: 110.0): ")
        lon_org = float(l_lon) if l_lon else 110.94
        
        l_dest = input("Latitud Destino (ej: 22.0): ")
        lat_dest = float(l_dest) if l_dest else 21.91
        
        l_dlon = input("Longitud Destino (ej: 69.5): ")
        lon_dest = float(l_dlon) if l_dlon else 69.45
        
        crane = input("ID Individuo (ej: 6235): ")
        crane_id = crane if crane else "Unknown"

        # 2. Appel Logique
        result = logic.req_1(
            control, 
            lat_org, lon_org, 
            lat_dest, lon_dest, 
            crane_id
        )

        # 3. Gestion Erreur
        if "error" in result:
            print(f"\n[!] {result['error']}")
            return

        # 4. Affichage Résumé
        print(f"\n> {result['message']}")
        print(f"> Distancia total estimada:   {result['total_dist']:.4f} km")
        print(f"> Total de puntos en camino:  {result['total_steps']}")
        
        # 5. Préparation Tableau (5 premiers / 5 derniers)
        details = result['details']
        headers = ["ID Punto", "Posición", "Num. Indiv.", "Muestra IDs", "Dist. Sig. (km)"]
        
        table_data = []
        
        if len(details) <= 10:
            # S'il y a 10 points ou moins, on affiche tout
            table_data = [_format_req1_row(d) for d in details]
        else:
            # 5 premiers
            table_data.extend([_format_req1_row(d) for d in details[:5]])
            # Séparateur
            table_data.append(["...", "...", "...", "...", "..."])
            # 5 derniers
            table_data.extend([_format_req1_row(d) for d in details[-5:]])
        
        print("\n--- Detalle de la Ruta (Primeros y Últimos) ---")
        print(tabulate(table_data, headers=headers, tablefmt="fancy_grid"))

    except ValueError:
        print("Error: Las coordenadas deben ser numéricas.")
    except Exception as e:
        print(f"Error inesperado: {e}")

# ==============================================================================
# MENU / CHARGEMENT
# ==============================================================================

def load_data(control):
    """
    Fonction de la vue qui appelle la logique et affiche le résultat.
    """
    filename = input("Nombre del archivo a cargar (ej: Data/1000_cranes_mongolia_small.csv): ")
    
    try:
        control = logic.load_data(control, filename)
        
        if control:
            print_load_report(control)
        else:
            print("Erreur lors du chargement des données (Catalogue vide).")
            
    except Exception as e:
        print(f"Une erreur est survenue : {e}")
        
    return control


def _format_req2_row(detail_dict):
    
    """
    Helper para formatear filas del req_2
    """
    
    dist_val = detail_dict['dist_next']
    if isinstance(dist_val, (int, float)) and dist_val > 0:
        dist_s = f"{dist_val:.4f}"
    else:
        dist_s = "-"
    
    return [
        detail_dict['id'],
        f"({detail_dict['lat']:.4f}, {detail_dict['lon']:.4f})",
        detail_dict['birds_count'],
        detail_dict['birds_sample'],
        dist_s
    ]

def print_req_2(control):
    """
    View para el req_2
    """
    print("\n" + "="*60)
    print("REQ. 2: Detectar movimientos alrededor de un área (BFS)")
    print("="*60)
    
    if control is None or 'graph_dist' not in control:
        print("Error: Debe cargar los datos primero.")
        return
    
    try:
        print("Ingrese coordenadas (Deje vacío para usar valores por defecto):")
        
        l_org = input("Latitud Origen (ej: 48.47): ")
        lat_org = float(l_org) if l_org else 48.47
        
        l_lon = input("Longitud Origen (ej: 110.94): ")
        lon_org = float(l_lon) if l_lon else 110.94
        
        l_dest = input("Latitud Destino (ej: 21.91): ")
        lat_dest = float(l_dest) if l_dest else 21.91
        
        l_dlon = input("Longitud Destino (ej: 69.45): ")
        lon_dest = float(l_dlon) if l_dlon else 69.45
        
        radius = input("Radio del área de interés en km (ej: 50): ")
        radius_km = float(radius) if radius else 50.0
        
        result = logic.req_2(
            control,
            lat_org, lon_org,
            lat_dest, lon_dest,
            radius_km
        )
        
        if "error" in result:
            print(f"\n[!] {result['error']}")
            return
        
        # Mostrar resumen
        print(f"\n> {result['message']}")
        print(f"> Distancia total estimada:   {result['total_dist']:.4f} km")
        print(f"> Total de puntos en camino:  {result['total_steps']}")
        
        # Preparar resultados
        details = result['details']
        headers = ["ID Punto", "Posición", "Num. Indiv.", "Muestra IDs", "Dist. Sig. (km)"]
        
        table_data = []
        
        if len(details) <= 10:
            table_data = [_format_req2_row(d) for d in details]
        else:
            table_data.extend([_format_req2_row(d) for d in details[:5]])
            table_data.append(["...", "...", "...", "...", "..."])
            table_data.extend([_format_req2_row(d) for d in details[-5:]])
        
        print("\n--- Detalle de la Ruta (Primeros y Últimos) ---")
        print(tabulate(table_data, headers=headers, tablefmt="fancy_grid"))
        
    except ValueError:
        print("Error: Las coordenadas y radio deben ser numéricos.")
    except Exception as e:
        print(f"Error inesperado: {e}")


def print_req_3(control):
    """
        Función que imprime la solución del Requerimiento 3 en consola
    """
    # TODO: Imprimir el resultado del requerimiento 3
    pass

def _format_req4_row(graph, node_id):
    """
    Helper pour Req 4 (Corridors Prim).
    Colonnes : ID, Pos, Nb Grullas, Liste IDs (3 premiers/3 derniers).
    """
    vertex_entry = mp.get(graph['vertices'], node_id)
    if not vertex_entry: 
        return ["Error", "", "", ""]
    
    info = vertex_entry['value']
    
    # Formatage spécifique : 3 premiers et 3 derniers IDs [cite: 354]
    birds = list(info['bird_ids'])
    if len(birds) > 6:
        birds_fmt = str(birds[:3] + birds[-3:])
    else:
        birds_fmt = str(birds)
    
    return [
        info['key'],
        f"({info['lat']:.4f}, {info['lon']:.4f})",
        info['event_count'],
        birds_fmt
    ]
    
def print_req_4(control):
    """
    Vue pour Req 4 : Prim MST.
    """
    print("\n" + "="*60)
    print("REQ. 4: Corredores hídricos óptimos (Prim MST)")
    print("="*60)
    
    if control is None or 'graph_water' not in control:
        print("Error: Cargue datos primero.")
        return

    try:
        print("Ingrese coordenadas de inicio (Enter para valores por defecto):")
        # Valeurs par défaut basées sur le premier point du fichier small
        l_lat = input("Latitud Origen (ej: 48.4753): ")
        lat_org = float(l_lat) if l_lat else 48.4753
        
        l_lon = input("Longitud Origen (ej: 110.9471): ")
        lon_org = float(l_lon) if l_lon else 110.9471

        # Appel Logique
        res = logic.req_4(control, lat_org, lon_org)
        
        if "error" in res:
            print(f"\n[!] {res['error']}")
            return

        # Affichage Résumé [cite: 345-347]
        print(f"\n> {res['message']}")
        print(f"> Total puntos en la ruta (MST):   {res['total_nodes']}")
        print(f"> Total individuos únicos:         {res['total_individuals']}")
        print(f"> Distancia Hídrica Total (Cost):  {res['total_cost']:.4f} m")
        
        # Tableau Détaillé [cite: 348]
        mst_ids = res['mst_order']
        graph_water = control['graph_water']
        
        headers = ["ID Punto", "Posición", "Tránsito (Eventos)", "Muestra IDs Grullas"]
        rows = []

        # Logique d'affichage 5 premiers / 5 derniers
        if len(mst_ids) <= 10:
            rows = [_format_req4_row(graph_water, nid) for nid in mst_ids]
        else:
            # 5 premiers
            rows.extend([_format_req4_row(graph_water, nid) for nid in mst_ids[:5]])
            # Séparateur
            rows.append(["...", "...", "...", "..."])
            # 5 derniers
            rows.extend([_format_req4_row(graph_water, nid) for nid in mst_ids[-5:]])

        print("\n--- Definición del Corredor (Primeros y Últimos) ---")
        print(tabulate(rows, headers=headers, tablefmt="fancy_grid"))

    except ValueError:
        print("Error: Las coordenadas deben ser numéricas.")
    except Exception as e:
        print(f"Error inesperado: {e}")


def print_req_5(control):
    """
        Función que imprime la solución del Requerimiento 5 en consola
    """
    # TODO: Imprimir el resultado del requerimiento 5
    pass


def print_req_6(control):
    """
        Función que imprime la solución del Requerimiento 6 en consola
    """
    # TODO: Imprimir el resultado del requerimiento 6
    pass

# Se crea la lógica asociado a la vista
control = new_logic()

# main del ejercicio
def main():
    """
    Menu principal
    """
    working = True
    #ciclo del menu
    while working:
        print_menu()
        inputs = input('Seleccione una opción para continuar\n')
        if int(inputs) == 0:
            print("Cargando información de los archivos ....\n")
            control=new_logic()
            data = load_data(control)
        elif int(inputs) == 1:
            print_req_1(control)

        elif int(inputs) == 2:
            print_req_2(control)

        elif int(inputs) == 3:
            print_req_3(control)

        elif int(inputs) == 4:
            print_req_4(control)

        elif int(inputs) == 5:
            print_req_5(control)

        elif int(inputs) == 5:
            print_req_6(control)

        elif int(inputs) == 7:
            working = False
            print("\nGracias por utilizar el programa") 
        else:
            print("Opción errónea, vuelva a elegir.\n")
    sys.exit(0)
