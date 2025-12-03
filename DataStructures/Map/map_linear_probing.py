import random
from DataStructures.List import array_list as al
from DataStructures.Map import map_entry as me
from DataStructures.Map import map_functions as mf


def new_map(num_elements, load_factor, prime=109345121):
    value = int(num_elements / load_factor)
    capacity = mf.next_prime(value)
    if capacity == 0:
        capacity = 3
    res = {
        'prime': prime,
        'capacity': capacity,
        'scale': random.randint(1, prime - 1),
        'shift': random.randint(1, prime - 1),
        'table': al.new_list(),
        'current_factor': 0,
        'limit_factor': load_factor,
        'size': 0
    }

    for _ in range(capacity):
        al.add_last(res["table"], me.new_map_entry(None, None))

    return res



def is_available(table, pos):

   entry = al.get_element(table, pos)
   if me.get_key(entry) is None or me.get_key(entry) == "__EMPTY__":
      return True
   return False


def find_slot(my_map, key, hash_value):
    first_avail = None
    while True:
        entry = al.get_element(my_map["table"], hash_value)
        k = me.get_key(entry)

        if k is None:  
            if first_avail is None:
                first_avail = hash_value
            return False, first_avail

        elif k == "__EMPTY__":  
            if first_avail is None:
                first_avail = hash_value

        elif k == key:
            return True, hash_value

        hash_value = (hash_value + 1) % my_map["capacity"]


def rehash(my_map):
    new_capacity = mf.next_prime(my_map["capacity"] * 2)
    new_table = new_map(new_capacity, my_map["limit_factor"], my_map["prime"])

    for i in range(my_map["capacity"]):
        entry = al.get_element(my_map["table"], i)
        key = me.get_key(entry)
        val = me.get_value(entry)
        if key is not None and key != "__EMPTY__":
            put(new_table, key, val)

    return new_table


def put(my_map, key, value):
    hash_val = mf.hash_value(my_map, key)
    found, pos = find_slot(my_map, key, hash_val)

    if found:
        entry = al.get_element(my_map["table"], pos)
        me.set_value(entry, value)
        al.change_info(my_map["table"], pos, entry)
    else:
        entry = me.new_map_entry(key, value)
        al.change_info(my_map["table"], pos, entry)
        my_map["size"] += 1
        my_map["current_factor"] = my_map["size"] / my_map["capacity"]

    if my_map["current_factor"] > my_map["limit_factor"]:
        my_map = rehash(my_map)

    return my_map


def get(my_map, key):
    hash_val = mf.hash_value(my_map, key)
    found, pos = find_slot(my_map, key, hash_val)
    if found:
        entry = al.get_element(my_map["table"], pos)
        return me.get_value(entry)
    return None


def contains(my_map, key):
    hash_val = mf.hash_value(my_map, key)
    found, pos = find_slot(my_map, key, hash_val)
    return found


def remove(my_map, key):
    hash_val = mf.hash_value(my_map, key)
    found, pos = find_slot(my_map, key, hash_val)

    if found:
        al.change_info(my_map["table"], pos, me.new_map_entry("__EMPTY__", "__EMPTY__"))
        my_map["size"] -= 1
        my_map["current_factor"] = my_map["size"] / my_map["capacity"]

    return my_map


def size(my_map):
    return my_map["size"]

def is_empty(my_map):
    return my_map["size"] == 0


def key_set(my_map):
    keys = al.new_list()
    table = my_map.get("table")

    elements = table.get("elements") if isinstance(table, dict) and "elements" in table else table

    for entry in elements:
        if isinstance(entry, dict):
            k = me.get_key(entry)
            if k is not None and k != "__EMPTY__":
                al.add_last(keys, k)

    return keys


def value_set(my_map):
    values = al.new_list()
    table = my_map.get("table")

    elements = table.get("elements") if isinstance(table, dict) and "elements" in table else table

    for entry in elements:
        if isinstance(entry, dict):
            k = me.get_key(entry)
            v = me.get_value(entry)
            if k is not None and k != "__EMPTY__" and v is not None:
                al.add_last(values, v)

    return values