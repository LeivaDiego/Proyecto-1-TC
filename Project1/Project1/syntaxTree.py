from graphviz import Digraph

class Node:
    # Definicion de los nodos del arbol

    def __init__(self, value):
        self.value = value
        self.children = []

class SyntaxTree(object):
    # Clase que modela y construye un arbol sintactico a partir de una expresion dada en formato postfix

    def build_tree(self, postfix):
        # Procesa la expresion caracter por caracter, utilizando una pila para realizar un seguimiento de los nodos
        stack = []

        for char in postfix:
            if char not in '*|^':
                new_node = Node(char)
                stack.append(new_node)

            elif char == '*':
                if len(stack) >= 1:
                    child = stack.pop()
                    new_node = Node(char)
                    new_node.children.append(child)
                    stack.append(new_node)

                else:
                    raise Exception("Invalid expression")

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

        return stack[0] if len(stack) == 1 else None


    def visualize_tree(self, root, dot=None):
        # Recorre el arbol de manera recursiva y crea nodos y aristas para la visualizacion usando graphviz
        if dot is None:
            dot = Digraph()
        if root:
            dot.node(str(id(root)), str(root.value))
            for child in root.children:
                dot.node(str(id(child)), str(child.value))
                dot.edge(str(id(root)), str(id(child)))
                self.visualize_tree(child, dot)
        return dot