from graphviz import Digraph


class State:
    #Clase para representar un estado en un AFN
    state_counter = 0

    def __init__(self):
        self.transitions = {}
        self.is_final = False
        self.state_number = None
        

    def add_transition(self, symbol, state):
        # Agregar una transicion para un simbolo a un estado dado
        if symbol not in self.transitions:
            self.transitions[symbol] = []
        if state not in self.transitions[symbol]:                                                                                                       
            self.transitions[symbol].append(state)



class AFN:
    #Clase para representar un Automata Finito No Determinista

    def __init__(self, start=None, end=None):
        self.start_state = start if start else State()
        self.end_state = end if end else State()
        self.end_state.is_final = True
    
    def assign_state_numbers(self):
        # Asignar números de estado de forma dinámica
        counter = 1
        states_to_visit = [self.start_state]
        visited_states = set()

        while states_to_visit:
            current_state = states_to_visit.pop()
            current_state.state_number = counter
            counter += 1

            for next_states in current_state.transitions.values():
                for next_state in next_states:
                    if next_state not in visited_states:
                        states_to_visit.append(next_state)

            visited_states.add(current_state)


    def connect_to(self, other_nfa, symbol=None):
        # Conectar el estado final de este AFN al estado inicial de otro AFN con un simbolo dado (por defecto es ε)
        self.end_state.add_transition(symbol, other_nfa.start_state)


    @staticmethod
    def from_symbol(symbol):
        # Crear un AFN basico a partir de un simbolo dado
        start = State()
        end = State()
        start.add_transition(symbol, end)

        return AFN(start, end)


    def visualize_afn(self):
    # Visualizar el AFN usando graphviz
        dot = Digraph()
        states_to_visit = [self.start_state]
        visited_states = set()

        while states_to_visit:
            current_state = states_to_visit.pop()

            for symbol, next_states in current_state.transitions.items():
                for next_state in next_states:
                    if current_state == self.start_state:
                        dot.node(str(id(current_state)), label=f"Inicio ({current_state.state_number})", shape="ellipse")
                    else:
                        dot.node(str(id(current_state)), label=str(current_state.state_number), shape="ellipse")

                    if next_state.is_final and next_state == self.end_state:
                        dot.node(str(id(next_state)), label=f"Fin ({next_state.state_number})", shape="doublecircle")
                    else:
                        dot.node(str(id(next_state)), label=str(next_state.state_number), shape="ellipse")

                    dot.edge(str(id(current_state)), str(id(next_state)), label=symbol if symbol else 'ε')

                    if next_state not in visited_states:
                        states_to_visit.append(next_state)

            visited_states.add(current_state)

        return dot





def thompson_from_tree(node):
    # Construir un AFN a partir de un nodo de árbol sintáctico usando la construcción de Thompson

    # Si el nodo es un literal
    if not node.children:
        return AFN.from_symbol(node.value)


    # Para el operador Kleene (*)
    if node.value == '*':
        internal_nfa = thompson_from_tree(node.children[0])
        start = State()
        end = State()

        # Transiciones epsilon
        start.add_transition(None, internal_nfa.start_state)  
        start.add_transition(None, end)  
        internal_nfa.end_state.add_transition(None, internal_nfa.start_state)  
        internal_nfa.end_state.add_transition(None, end)

        return AFN(start, end)


    # Para el operador de alternancia (|)
    if node.value == '|':
        left_nfa = thompson_from_tree(node.children[0])
        right_nfa = thompson_from_tree(node.children[1])
        start = State()
        end = State()

        # Transiciones epsilon
        start.add_transition(None, left_nfa.start_state)  
        start.add_transition(None, right_nfa.start_state)
        left_nfa.end_state.add_transition(None, end)  
        right_nfa.end_state.add_transition(None, end)  

        return AFN(start, end)


    # Para el operador de concatenación (^)
    if node.value == '^':
        left_nfa = thompson_from_tree(node.children[0])
        right_nfa = thompson_from_tree(node.children[1])
        # Conectar el final de la izquierda al inicio de la derecha con transición epsilon
        left_nfa.connect_to(right_nfa) 

        return AFN(left_nfa.start_state, right_nfa.end_state)


def simulate_afn(afn, input_string):
    # Inicializar los estados actuales con solo el estado inicial
    current_states = set([afn.start_state])

    # Ampliar los estados actuales para incluir cualquier estado alcanzable mediante transiciones epsilon
    current_states = epsilon_closure(current_states)

    # Para cada símbolo en la cadena de entrada
    for symbol in input_string:
        # Calcular los estados siguientes basados en los estados actuales y el símbolo de entrada
        next_states = set()
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
            return True

    return False


def epsilon_closure(states):

    # Utilizar una pila para llevar un registro de los estados que necesitan ser procesados
    stack = list(states)
    epsilon_closure = set(states)

    while stack:
        state = stack.pop()
        if None in state.transitions:
            for next_state in state.transitions[None]:
                if next_state not in epsilon_closure:
                    epsilon_closure.add(next_state)
                    stack.append(next_state)

    return epsilon_closure