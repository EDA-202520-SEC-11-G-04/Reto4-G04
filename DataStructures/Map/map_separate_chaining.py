import random
from DataStructures.List import array_list as al
from DataStructures.Map import map_entry as me
from DataStructures.Map import map_functions as mf


def new_map(num_elements, load_factor, prime=109345121):
    """
    Crea un nuevo mapa (Separate Chaining).
    """
    target = int(num_elements / load_factor) if load_factor > 0 else int(num_elements)
    if target <= 0:
        target = 3
    if mf.is_prime(target):
        capacity = target
    else:
        capacity = mf.next_prime(target)

    m = {
        "prime": prime,
        "capacity": capacity,
        "scale": random.randint(1, prime - 1),
        "shift": random.randint(0, prime - 1),
        "table": al.new_list(),
        "limit_factor": load_factor,
        "size": 0
    }

    # Inicializar lista principal con cadenas vacías
    for _ in range(capacity):
        chain = al.new_list()
        al.add_last(m["table"], chain)

    return m


def get_bucket(my_map, key):
    """
    Devuelve la cadena (bucket) correspondiente al hash de la llave.
    """
    index = mf.hash_value(my_map, key)
    chain = al.get_element(my_map["table"], index)
    return chain, index


def put(my_map, key, value):
    """
    Inserta o actualiza un par (key, value) en el mapa.
    """
    chain, index = get_bucket(my_map, key)

    # Verificar si la llave ya existe en la cadena
    for i in range(al.size(chain)):
        entry = al.get_element(chain, i)
        if me.get_key(entry) == key:
            me.set_value(entry, value)
            return my_map

    # Si no existe, agregar un nuevo entry
    new_entry = me.new_map_entry(key, value)
    al.add_last(chain, new_entry)
    my_map["size"] += 1

    # Rehash si excede el factor de carga
    current_factor = my_map["size"] / my_map["capacity"]
    if current_factor > my_map["limit_factor"]:
        my_map = rehash(my_map)

    return my_map


def get(my_map, key):
    chain, _ = get_bucket(my_map, key)
    for i in range(al.size(chain)):
        entry = al.get_element(chain, i)
        if me.get_key(entry) == key:
            return me.get_value(entry)
    return None


def contains(my_map, key):
    chain, _ = get_bucket(my_map, key)
    for i in range(al.size(chain)):
        entry = al.get_element(chain, i)
        if me.get_key(entry) == key:
            return True
    return False


def remove(my_map, key):
    chain, _ = get_bucket(my_map, key)
    for i in range(al.size(chain)):
        entry = al.get_element(chain, i)
        if me.get_key(entry) == key:
            al.delete_element(chain, i)
            my_map["size"] -= 1
            return my_map
    return my_map


def size(my_map):
    return my_map["size"]


def is_empty(my_map):
    return my_map["size"] == 0


def key_set(my_map):
    keys = al.new_list()
    for i in range(my_map["capacity"]):
        chain = al.get_element(my_map["table"], i)
        for j in range(al.size(chain)):
            entry = al.get_element(chain, j)
            al.add_last(keys, me.get_key(entry))
    return keys


def value_set(my_map):
    values = al.new_list()
    for i in range(my_map["capacity"]):
        chain = al.get_element(my_map["table"], i)
        for j in range(al.size(chain)):
            entry = al.get_element(chain, j)
            al.add_last(values, me.get_value(entry))
    return values


def rehash(my_map):
    old_table = my_map["table"]
    old_capacity = my_map["capacity"]

    new_capacity = mf.next_prime(2 * old_capacity)

    new_table = al.new_list()
    for _ in range(new_capacity):
        al.add_last(new_table, al.new_list())

    count = 0
    for i in range(al.size(old_table)):
        bucket = al.get_element(old_table, i)
        for j in range(al.size(bucket)):
            entry = al.get_element(bucket, j)
            key = me.get_key(entry)
            value = me.get_value(entry)
            if key is not None and key != "__EMPTY__":
                pos = mf.hash_value(my_map, key)
                pos = (pos % new_capacity)
                bucket_new = al.get_element(new_table, pos)
                al.add_last(bucket_new, me.new_map_entry(key, value))
                count += 1

    my_map["capacity"] = new_capacity
    my_map["table"] = new_table
    my_map["size"] = count

    return my_map
