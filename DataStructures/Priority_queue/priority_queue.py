from DataStructures.Priority_queue import pq_entry as pqe
from DataStructures.List import array_list as lt

def default_compare_lower_value(father_node, child_node):
    return pqe.get_priority(father_node) <= pqe.get_priority(child_node)

def default_compare_higher_value(father_node, child_node):
    return pqe.get_priority(father_node) >= pqe.get_priority(child_node)

def new_heap(is_min_pq=True):
    cmp_function = default_compare_lower_value if is_min_pq else default_compare_higher_value
    heap = {
        "elements": lt.new_list(),
        "size": 0,
        "cmp_function": cmp_function
    }
    lt.add_last(heap["elements"], None)
    return heap

def size(my_heap):
    return my_heap["size"]

def is_empty(my_heap):
    return size(my_heap) == 0

def priority(my_heap, parent, child):
    return my_heap["cmp_function"](parent, child)

def exchange(my_heap, i, j):
    lt.exchange(my_heap["elements"], i, j)

def swim(my_heap, pos):
    elems = my_heap["elements"]
    while pos > 1:
        parent_pos = pos // 2
        parent_elem = lt.get_element(elems, parent_pos)
        child_elem = lt.get_element(elems, pos)
        if not priority(my_heap, parent_elem, child_elem):
            exchange(my_heap, parent_pos, pos)
            pos = parent_pos
        else:
            break

def insert(my_heap, priority_value, value):
    entry = pqe.new_pq_entry(priority_value, value)
    lt.add_last(my_heap["elements"], entry)
    my_heap["size"] += 1
    swim(my_heap, my_heap["size"])
    return my_heap

def get_first_priority(my_heap):
    if is_empty(my_heap):
        return None
    first = lt.get_element(my_heap["elements"], 1)
    return pqe.get_value(first)

def sink(my_heap, pos):
    elems = my_heap["elements"]
    size = my_heap["size"]
    while 2 * pos <= size:
        child = 2 * pos
        if child < size:
            left = lt.get_element(elems, child)
            right = lt.get_element(elems, child + 1)
            if not priority(my_heap, left, right):
                child += 1
        parent_elem = lt.get_element(elems, pos)
        child_elem = lt.get_element(elems, child)
        if priority(my_heap, parent_elem, child_elem):
            break
        exchange(my_heap, pos, child)
        pos = child

def remove(my_heap):
    if is_empty(my_heap):
        return None
    elems = my_heap["elements"]
    first_elem = lt.get_element(elems, 1)
    last_elem = lt.get_element(elems, my_heap["size"])
    lt.exchange(elems, 1, my_heap["size"])

    lt.remove_last(elems)
    my_heap["size"] -= 1
    if my_heap["size"] > 0:
        sink(my_heap, 1)
    return pqe.get_value(first_elem)

def is_present_value(my_heap, value):
    elems = my_heap["elements"]
    size = my_heap["size"]
    for i in range(1, size + 1):
        elem = lt.get_element(elems, i)
        if pqe.get_value(elem) == value:
            return i
    return -1

def contains(my_heap, value):
    return is_present_value(my_heap, value) != -1
