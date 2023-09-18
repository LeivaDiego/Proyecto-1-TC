from graphviz import Digraph

# Clase que define los nodos del arbol sintactico.
# Cada nodo tiene un valor y una lista de hijos.
class Node:

    def __init__(self, value):
        self.value = value
        self.children = []



# Clase que modela y construye un arbol sintactico a partir de una expresion dada en formato postfix
class SyntaxTree(object):

    # Procesa la expresion caracter por caracter, utilizando una pila para realizar un seguimiento de los nodos
    def build_tree(self, postfix):
        
        stack = [] # Pila para mantener un registro de los nodos mientras se construye el arbol

        # recorre cada caracter de la expresion postfix
        for char in postfix:

            # Si el caracter es un operando, crea un nuevo nodo y lo agrega a la pila
            if char not in '*|^':
                new_node = Node(char)
                stack.append(new_node)
            
            # Si el caracter es '*', crea un nuevo nodo y lo asigna como hijo del nodo anterior
            elif char == '*':
                if len(stack) >= 1:
                    child = stack.pop()
                    new_node = Node(char)
                    new_node.children.append(child)
                    stack.append(new_node)
                else:
                    raise Exception("Invalid expression")

            # Si el caracter es '|' o '^', crea un nuevo nodo y asigna los dos nodos anteriores como hijos
            elif char in "|^":
                if len(stack) >= 2:
                    new_node = Node(char)
                    right_child = stack.pop()
                    left_child = stack.pop()
                    new_node.children.append(left_child)
                    new_node.children.append(right_child)
                    stack.append(new_node)
                else:
                    raise Exception("Invalid expression")

        # Devuelve la raiz del arbol si se ha construido correctamente
        return stack[0] if len(stack) == 1 else None


    # Visualiza el arbol sintactico utilizando la libreria Graphviz.
    def visualize_tree(self, root, dot=None):

        # Inicializa el objeto Digraph si no se proporciona
        if dot is None:
            dot = Digraph()

        # Si el nodo raiz existe, procede a visualizar
        if root:
             # Crea un nodo en el grafico para la raiz
            dot.node(str(id(root)), str(root.value))

            # Recorre cada hijo de la raiz y crea nodos y aristas en el grafico
            for child in root.children:
                dot.node(str(id(child)), str(child.value))
                dot.edge(str(id(root)), str(id(child)))
                self.visualize_tree(child, dot) # Llamada recursiva para visualizar subarboles
        return dot