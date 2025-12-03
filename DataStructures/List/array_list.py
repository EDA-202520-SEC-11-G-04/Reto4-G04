def new_list():
    newlist={
        'elements':[],
        'size':0,
    }
    return newlist

def get_element(my_list, index):
    return my_list["elements"][index]

def is_present(my_list,element, cmp_function):
    size=my_list["size"]
    if size>0:
        keyexist=False
        for keypos in range(0,size):
            info=my_list["elements"][keypos]
            if cmp_function(element,info)==0:
                keyexist=True
                break
            if keyexist:
                return keypos
    return -1

def add_first(my_list,element):
     my_list["elements"].insert(0, element)  
     my_list["size"] += 1
     return my_list

def add_last(my_list,element):
    my_list["elements"].append(element)
    my_list["size"] += 1    
    return my_list

def size(my_list):
    return my_list["size"]

def first_element(my_list):
    return my_list["elements"][0]

def is_empty(my_list):
    empty=False
    if my_list["size"]==0:
        empty=True
    return empty
        
def last_element(my_list):
    return my_list["elements"][size(my_list)-1]

def delete_element(my_list, pos):
    my_list["elements"].pop(pos)
    my_list["size"]-=1
    return my_list
    
    
def remove_first(my_list):
    val=my_list["elements"].pop(0)
    my_list["size"]-=1
    return val

def remove_last(my_list):
    val=my_list["elements"].pop()
    my_list["size"]-=1
    return val
 
def insert_element(my_list, element, pos):
    my_list["elements"].insert(element,pos)
    my_list["size"]+=1
    return my_list

def change_info(my_list, pos, new_info):
    my_list["elements"][pos]=new_info
    return my_list

def exchange(my_list, pos1, pos2):
    x=my_list["elements"][pos1]
    my_list["elements"][pos1]=my_list["elements"][pos2]
    my_list["elements"][pos2]=x
    return my_list

def sub_list(my_list, pos_i, num_elements):
    sub=new_list()
    sub["size"]=num_elements
    sub["elements"]=my_list["elements"][pos_i:pos_i+num_elements]
    return sub

def default_sort_criteria(element_1, element_2):

   is_sorted = False
   if element_1 < element_2:
      is_sorted = True
   return is_sorted

def selection_sort(my_list, sort_crit=default_sort_criteria):
    n = my_list["size"]
    for i in range(n):
        min_index = i
        for j in range(i+1, n):
            if not sort_crit(my_list["elements"][min_index], my_list["elements"][j]):
                min_index = j
        # échange
        my_list["elements"][i], my_list["elements"][min_index] = my_list["elements"][min_index], my_list["elements"][i]
    return my_list

        
def insertion_sort(my_list, sort_crit):
    
    for i in range(1, my_list['size']):
        key = my_list['elements'][i] 
        j = i - 1

        while j >= 0 and not sort_crit(my_list['elements'][j], key):
            my_list['elements'][j + 1] = my_list['elements'][j]
            j -= 1

        my_list['elements'][j + 1] = key

    return my_list                

def shell_sort(my_list, sort_crit=default_sort_criteria):
    n = my_list["size"]
    gap = n // 2 

    while gap > 0:
        for i in range(gap, n):
            temp = my_list["elements"][i]
            j = i
            while j >= gap and not sort_crit(my_list["elements"][j - gap], temp):
                my_list["elements"][j] = my_list["elements"][j - gap]
                j -= gap

            my_list["elements"][j] = temp

        gap //= 2 
    return my_list


def merge_sort(my_list, sort_crit=default_sort_criteria):
    if my_list["size"] <= 1:
        return my_list

    mid = my_list["size"] // 2
    left = {"elements": my_list["elements"][:mid], "size": mid}
    right = {"elements": my_list["elements"][mid:], "size": my_list["size"] - mid}

    left_sorted = merge_sort(left, sort_crit)
    right_sorted = merge_sort(right, sort_crit)

    return merge_array_lists(left_sorted, right_sorted, sort_crit)


def merge_array_lists(left, right, sort_crit):
    result = []
    i = j = 0
    while i < left["size"] and j < right["size"]:
        if sort_crit(left["elements"][i], right["elements"][j]):
            result.append(left["elements"][i])
            i += 1
        else:
            result.append(right["elements"][j])
            j += 1

    result.extend(left["elements"][i:])
    result.extend(right["elements"][j:])

    return {"elements": result, "size": len(result)}

def quick_sort(my_list, sort_crit=default_sort_criteria):
    if my_list["size"] <= 1:
        return my_list

    pivot = my_list["elements"][0]
    menor = []
    igual = []
    mayor = []

    for elem in my_list["elements"]:
        if sort_crit(elem, pivot) and elem != pivot:
            menor.append(elem)
        elif sort_crit(pivot, elem) and elem != pivot:
            mayor.append(elem)
        else:
            igual.append(elem)

    menor_list = {"elements": menor, "size": len(menor)}
    mayor_list = {"elements": mayor, "size": len(mayor)}

    menor_sorted = quick_sort(menor_list, sort_crit)
    mayor_sorted = quick_sort(mayor_list, sort_crit)

    sorted_elements = menor_sorted["elements"] + igual + mayor_sorted["elements"]

    return {"elements": sorted_elements, "size": len(sorted_elements)}
