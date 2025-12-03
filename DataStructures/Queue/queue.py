from DataStructures.List import array_list as lt
#from DataStructures.List import single_linked_list as lt

def new_queue():

    return lt.new_list()

def size(my_queue):
    
    return lt.size(my_queue)

def is_empty(my_queue):
    return lt.is_empty(my_queue)
        
def enqueue(my_queue, element):

    lt.add_last(my_queue, element)
    return my_queue

def dequeue(my_queue):
    if lt.is_empty(my_queue):
        raise Exception("EmptyStructureError: queue is empty")
    return lt.remove_first(my_queue)

def peek(my_queue):
    if lt.is_empty(my_queue):
        raise Exception("EmptyStructureError: queue is empty")
    return lt.first_element(my_queue)#["info"]

