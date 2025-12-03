def new_list():
    newlist={
        "first":None,
        "last":None,
        "size":0,
    }
    return newlist

def get_element(my_list, pos):
    searchpos=0
    node=my_list["first"]
    while searchpos<pos:
        node=node["next"]
        searchpos+=1
    return node["info"]

def is_present(my_list,element,cmp_function):
    is_in_array=False
    temp=my_list["first"]
    count=0
    while not is_in_array and temp is not None:
        if cmp_function(element,temp["info"])==0:
            is_in_array=True
        else:
            temp=temp["next"]
            count+=1
    if not is_in_array:
        count=-1
    return count
    
def add_first(my_list,element):
    new_node = {"info": element, "next": None}

    if my_list["size"] == 0:  # si la liste est vide
        my_list["first"] = new_node
        my_list["last"] = new_node
    else:  # si déjà des éléments
        new_node["next"] = my_list["first"]
        my_list["first"] = new_node

    my_list["size"] += 1
    return my_list

def add_last(my_list, element):
    new_node = {"info": element, "next": None}

    if my_list["size"] == 0:  # si la liste est vide
        my_list["first"] = new_node
        my_list["last"] = new_node
    else:  # si déjà des éléments
        my_list["last"]["next"] = new_node
        my_list["last"] = new_node  # <- Important !
    my_list["size"] += 1
    return my_list


def size(my_list):
    return my_list["size"]

def first_element(my_list):
    if my_list["first"] is None:
        raise Exception('IndexError: list index out of range')
    return my_list["first"]

def is_empty(my_list):
    empty=False
    if my_list["first"] is None:
        empty=True
    return empty
        
def last_element(my_list):
    return my_list["last"]

def delete_element(my_list, pos):
    if pos < 0 or pos >= my_list["size"]:
        raise Exception("IndexError: list index out of range")

    if pos == 0:
        my_list["first"] = my_list["first"]["next"]
        if my_list["size"] == 1:  
            my_list["last"] = None
    else:
        current = my_list["first"]
        index = 0
        while index < pos - 1:
            current = current["next"]
            index += 1
        to_delete = current["next"]
        current["next"] = to_delete["next"]
        if pos == my_list["size"] - 1: 
            my_list["last"] = current

    my_list["size"] -= 1
    result = my_list
    return result
    
def remove_first(my_list):
    val=my_list["first"]["info"]
    if my_list["size"]==1:
        my_list["size"]=0
        my_list["first"]=None
        my_list["last"]=None
    else:
        my_list["first"]=my_list["first"]["next"]
        my_list["size"]-=1
    return val
     
def remove_last(my_list):
    removed=my_list["last"]["info"]
    if my_list["size"] == 1:
        removed = my_list["first"]["info"]
        my_list["first"] = None
        my_list["last"] = None
        my_list["size"] = 0
    else:
        current = my_list["first"]
        while current["next"] is not my_list["last"]:
            current = current["next"]
        current["next"] = None
        my_list["last"] = current
        my_list["size"] -= 1

    return removed

def insert_element(my_list, element, pos):
    if pos < 0 or pos > my_list["size"]:
        raise Exception("IndexError: list index out of range")

    new_node = {"info": element, "next": None}

    if pos == 0:  
        new_node["next"] = my_list["first"]
        my_list["first"] = new_node
        if my_list["size"] == 0:
            my_list["last"] = new_node
    elif pos == my_list["size"]:  
        my_list["last"]["next"] = new_node
        my_list["last"] = new_node
    else:  
        current = my_list["first"]
        index = 0
        while index < pos - 1:
            current = current["next"]
            index += 1
        new_node["next"] = current["next"]
        current["next"] = new_node

    my_list["size"] += 1
    return my_list

def change_info(my_list, pos, new_info):
    if pos < 0 or pos >= my_list["size"]:
        raise Exception("IndexError: list index out of range")

    current = my_list["first"]
    index = 0
    while index < pos:
        current = current["next"]
        index += 1

    current["info"] = new_info
    return my_list

def exchange(my_list, pos_1, pos_2):
    if (pos_1 < 0 or pos_1 >= my_list["size"] or
        pos_2 < 0 or pos_2 >= my_list["size"]):
        raise Exception("IndexError: list index out of range")

    if pos_1 == pos_2:
        return my_list

    node1 = my_list["first"]
    node2 = my_list["first"]
    index = 0
    while index < pos_1:
        node1 = node1["next"]
        index += 1
    index = 0
    while index < pos_2:
        node2 = node2["next"]
        index += 1
    
    x=node1["info"]
    node1["info"]=node2["info"]
    node2["info"]=x

    return my_list

def sub_list(my_list, pos, num_elements):
    if pos < 0 or pos >= my_list["size"]:
        raise Exception("IndexError: list index out of range")

    sub = new_list()
    current = my_list["first"]
    index = 0
    
    while index < pos:
        current = current["next"]
        index += 1

    count = 0
    while current is not None and count < num_elements:
        add_last(sub, current["info"])
        current = current["next"]
        count += 1

    return sub
