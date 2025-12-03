from DataStructures.List import array_list as lt
#from DataStructures.List import single_linked_list as lt

def new_stack():
   
    return lt.new_list()


def push(my_stack, element):

    lt.add_first(my_stack, element)
    return my_stack


def pop(my_stack):
    if lt.is_empty(my_stack):
        raise Exception("EmptyStructureError: stack is empty")
    return lt.remove_first(my_stack)

   
def top(my_stack):
    if lt.is_empty(my_stack):
        raise Exception("EmptyStructureError: stack is empty")
    return lt.first_element(my_stack)#["info"]


def is_empty(my_stack):

    return lt.is_empty(my_stack)


def size(my_stack):

    return lt.size(my_stack)
