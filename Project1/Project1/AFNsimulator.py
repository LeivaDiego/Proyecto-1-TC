from graphviz import Digraph

# Clase para representar un estado en un AFN (Automata Finito No determinista).
class State:
    
    state_counter = 0 # Contador para asignar numeros a los estados

    def __init__(self):
        self.transitions = {}       # Diccionario para almacenar transiciones
        self.is_final = False       # Indica si el estado es final
        self.state_number = None    # Numero del estado
        

    # Agregar una transicion para un simbolo a un estado dado
    def add_transition(self, symbol, state):

        # si el caracter no esta en las transisiones, se agrega
        if symbol not in self.transitions:
            self.transitions[symbol] = []
        # si el estado no esta dentro del listado, tambien se agrega
        if state not in self.transitions[symbol]:                                                                                                       
            self.transitions[symbol].append(state)



# Clase para representar un Automata Finito No determinista (AFN).
class AFN:

    # Inicializacion de un AFN nuevo-
    def __init__(self, start=None, end=None):
      
        self.start_state = start if start else State()
        self.end_state = end if end else State()
        self.end_state.is_final = True
    

    # Asignar numeros de estado de forma dinamica
    def assign_state_numbers(self):
        
        counter = 1                              # Contador para asignar numeros de estado
        states_to_visit = [self.start_state]     # Lista de estados por visitar
        visited_states = set()                   # Conjunto de estados ya visitados

        # Mientras haya estados por visitar
        while states_to_visit:
            # Tomar un estado de la lista
            current_state = states_to_visit.pop()
            # Asignarle un numero
            current_state.state_number = counter
            counter += 1 # Incrementar el contador de estados

            # Agregar los estados siguientes a la lista de estados por visitar
            for next_states in current_state.transitions.values():
                for next_state in next_states:
                    if next_state not in visited_states:
                        states_to_visit.append(next_state)
            
            # Marcar el estado actual como visitado
            visited_states.add(current_state)


    # Conectar el estado final de este AFN al estado inicial de otro AFN con un simbolo dado (por defecto es ε)
    def connect_to(self, other_nfa, symbol=None):

        # Agregar una transicion desde el estado final de este AFN al estado inicial del otro AFN
        self.end_state.add_transition(symbol, other_nfa.start_state)


    # Crear un AFN basico a partir de un simbolo dado
    @staticmethod
    def from_symbol(symbol):

        # Crear estados inicial y final
        start = State()
        end = State()
        # Agregar una transicion desde el estado inicial al estado final con el símbolo dado.
        start.add_transition(symbol, end)

        # Retornar un nuevo AFN con estos estados
        return AFN(start, end)


    # Visualiza el AFN usando la libreria Graphviz
    def visualize_afn(self):
    
        dot = Digraph()                         # Crear un nuevo grafo dirigido
        states_to_visit = [self.start_state]    # Lista de estados por visitar.
        visited_states = set()                  # Conjunto de estados ya visitados

        # Mientras haya estados por visitar
        while states_to_visit:
            # Tomar un estado de la lista
            current_state = states_to_visit.pop()

            # Agregar nodos y aristas al grafo
            for symbol, next_states in current_state.transitions.items():
                for next_state in next_states:
                    # Agregar nodos con etiquetas y formas adecuadas
                    if current_state == self.start_state:
                        dot.node(str(id(current_state)), label=f"Inicio ({current_state.state_number})", shape="ellipse")
                    else:
                        dot.node(str(id(current_state)), label=str(current_state.state_number), shape="ellipse")

                    if next_state.is_final and next_state == self.end_state:
                        dot.node(str(id(next_state)), label=f"Fin ({next_state.state_number})", shape="doublecircle")
                    else:
                        dot.node(str(id(next_state)), label=str(next_state.state_number), shape="ellipse")

                    # Agregar aristas con etiquetas adecuadas
                    dot.edge(str(id(current_state)), str(id(next_state)), label=symbol if symbol else 'ε')

                    # Agregar el estado siguiente a la lista de estados por visitar si no ha sido visitado
                    if next_state not in visited_states:
                        states_to_visit.append(next_state)

            # Marcar el estado actual como visitado
            visited_states.add(current_state)

        # Retornar el grafo
        return dot




# Construir un AFN a partir de un nodo de árbol sintáctico usando la construcción de Thompson
def thompson_from_tree(node):

    # Si el nodo es un literal construye un AFN para la literal
    if not node.children:
        # Retornar el nuevo AFN
        return AFN.from_symbol(node.value)

    # Para el operador Kleene '*' construye un AFN interno de forma recursiva
    if node.value == '*':
        internal_nfa = thompson_from_tree(node.children[0])
        # Asegurarse de que el estado final del AFN interno no este marcado como final
        internal_nfa.end_state.is_final = False
        # Crea los estados iniciales y finales de este AFN interno
        start = State()
        end = State()
        # Agregar las transiciones epsilon para el operador kleene '*'
        start.add_transition(None, internal_nfa.start_state)  
        start.add_transition(None, end)  
        internal_nfa.end_state.add_transition(None, internal_nfa.start_state)  
        internal_nfa.end_state.add_transition(None, end)
        # Retornar el nuevo AFN
        return AFN(start, end)

    # Para el operador de alternancia '|' construye un AFN izquiero y derecho de forma recursivca
    if node.value == '|':
        left_nfa = thompson_from_tree(node.children[0])
        right_nfa = thompson_from_tree(node.children[1])
        # Asegurarse de que los estados finales de ambos AFN no esten marcados como finales
        left_nfa.end_state.is_final = False
        right_nfa.end_state.is_final = False
        # Crea los estados iniciales y finales de estos AFN internos
        start = State()
        end = State()
        # Agregar las transiciones epsilon para el operador de alternancia '|'
        start.add_transition(None, left_nfa.start_state)  
        start.add_transition(None, right_nfa.start_state)
        left_nfa.end_state.add_transition(None, end)  
        right_nfa.end_state.add_transition(None, end)  
        # Retornar el nuevo AFN
        return AFN(start, end)

    # Para el operador de concatenacion '^' construye un AFN izquierdo y derecho de forma recursiva
    if node.value == '^':
        left_nfa = thompson_from_tree(node.children[0])
        right_nfa = thompson_from_tree(node.children[1])
        # Asegurarse de que el estado final del AFN de la izquierda no este marcado como final
        left_nfa.end_state.is_final = False
        # Conectar el final de la izquierda al inicio de la derecha con transicion epsilon
        left_nfa.connect_to(right_nfa) 
        # Retornar el nuevo AFN
        return AFN(left_nfa.start_state, right_nfa.end_state)


# Simular el recorrido del AFN para una cadena de entrada dada.
def simulate_afn(afn, input_string):

    # Inicializar los estados actuales con solo el estado inicial
    current_states = set([afn.start_state])

    # Ampliar los estados actuales para incluir cualquier estado alcanzable mediante transiciones epsilon
    current_states = epsilon_closure(current_states)

    # Recorrer cada simbolo de la cadena de entrada
    for symbol in input_string:
        # Calcular los estados siguientes basados en los estados actuales y el simbolo de entrada
        next_states = set() # Conjunto para almacenar los estados siguientes
        for state in current_states:
            if symbol in state.transitions:
                for next_state in state.transitions[symbol]:
                    next_states.add(next_state)
        # Ampliar los estados siguientes para incluir cualquier estado alcanzable mediante transiciones epsilon
        next_states = epsilon_closure(next_states)
        current_states = next_states

    # El AFN acepta la cadena de entrada si alguno de los estados actuales es un estado de aceptación
    for state in current_states:
        if state.is_final:
            return True # la cadena es aceptada

    return False # la cadena no es aceptada


# Calcula el cierre epsilon de un conjunto de estados
def epsilon_closure(states):
    
    stack = list(states)            # Pila para estados pendientes de procesar
    epsilon_closure = set(states)   # Conjunto para almacenar el cierre epsilon

    # Procesa cada estado en la pila
    while stack:
        state = stack.pop()
        # Si el estado tiene transiciones epsilon
        if None in state.transitions:
            for next_state in state.transitions[None]:
                # Si el estado siguiente no esta en el cierre epsilon
                if next_state not in epsilon_closure:
                    epsilon_closure.add(next_state) # Agregar al cierre epsilon
                    stack.append(next_state)        # Agregar a la pila para procesar

    # Retornar el cierre epsilon
    return epsilon_closure