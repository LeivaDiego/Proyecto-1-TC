from graphviz import Digraph

# Clase para representar un Automata Finito Determinista (AFD).
class AFD:

    # Inicializador de un nuedo AFD
    def __init__(self):

        self.states = []            # Lista de estados en el AFD
        self.start_state = None     # Estado inicial del AFD
        self.end_states = []        # Lista de estados finales del AFD


    # Agrega un estado al AFD
    def add_state(self, state):

        # Agregar el estado a la lista de estados
        self.states.append(state)

        # Si el estado es un estado final, agregarlo a la lista de estados finales.
        if state.is_final:
            self.end_states.append(state)


    # Visualiza el AFD usando la libreria Graphviz 
    def visualize_afd(self):

            dot = Digraph() # Crear un nuevo grafo dirigido con Graphviz
            
            # Recorrer cada estado en la lista de estados
            for state in self.states:
                 # Si el estado es final, usar un doble circulo para representarlo
                if state.is_final:
                    dot.node(str(id(state)), label=f"{state.state_number}", shape="doublecircle")
                # Si no, representarlo con una elipse
                else:
                    dot.node(str(id(state)), label=str(state.state_number), shape="ellipse")
                
                # Recorrer cada transicion del estado
                for symbol, next_state in state.transitions.items():
                    # Agregar una arista en el grafo para representar la transicion
                    dot.edge(str(id(state)), str(id(next_state)), label=symbol)
            
            # devolver el grafo
            return dot



# Clase que representa un estado del AFD
class AFDState:

    # Inicializa un nuevo estado
    def __init__(self, afn_states):
        
        self.afn_states = afn_states
        self.transitions = {}                                           # Transiciones desde este estado
        self.is_final = any(state.is_final for state in afn_states)     # Es un estado final si/no
        self.state_number = None                                        # Numero del estado


    # Agrega una transicion del estado dado
    def add_transition(self, symbol, state):
        
        self.transitions[symbol] = state



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


# Convierte un AFN dado a un AFD mediante el algoritmo de construccion de subconjuntos
def convert_to_afd(afn):
    
    afd = AFD() # Crear un nuevo objecto AFD

    # Obtener el cierre epsilon del estado inicial del AFN
    initial_afn_states = epsilon_closure(set([afn.start_state]))
    # Crear el estado inicial del AFD
    initial_afd_state = AFDState(initial_afn_states)
    initial_afd_state.state_number = 1      # Asignar numero de estado
    afd.start_state = initial_afd_state     # Establecer como estado inicial del AFD
    afd.add_state(initial_afd_state)        # Agregar al AFD

    unprocessed_states = [initial_afd_state]    # Lista de estados sin procesar
    counter = 2     # Contador para asignar numeros de estado

    # Mientras haya estados sin procesar
    while unprocessed_states:
        # Tomar un estado sin procesar
        current_afd_state = unprocessed_states.pop()

        symbols = set() # Conjunto para almacenar simbolos de transicion
        
        # Recopilar todos los simbolos de transicion de los estados del AFN correspondientes
        for afn_state in current_afd_state.afn_states:
            symbols.update(afn_state.transitions.keys())

        # Eliminar transiciones epsilon (None o ε)
        if None in symbols or 'ε' in symbols:
            symbols.remove(None)

        # Para cada simbolo de transicion
        for symbol in symbols:
            new_afn_states = set() # Conjunto para nuevos estados del AFN
            
            # Obtener todos los estados del AFN alcanzables con el simbolo actual
            for afn_state in current_afd_state.afn_states:
                if symbol in afn_state.transitions:
                    new_afn_states.update(afn_state.transitions[symbol])
            
            # Obtener el cierre epsilon de los nuevos estados del AFN
            new_afn_states = epsilon_closure(new_afn_states)

             # Verificar si el nuevo conjunto de estados del AFN ya existe en el AFD
            existing_state = next((state for state in afd.states if state.afn_states == new_afn_states), None)
            
            # Si no existe, crear un nuevo estado en el AFD
            if existing_state is None:
                new_afd_state = AFDState(new_afn_states)
                new_afd_state.state_number = counter 
                counter += 1
                afd.add_state(new_afd_state)
                unprocessed_states.append(new_afd_state)
                current_afd_state.add_transition(symbol, new_afd_state)
            # Si existe, agregar una transición al estado existente
            else:
                current_afd_state.add_transition(symbol, existing_state)
    
    # retornar el afd resultante
    return afd


# Simula el recorrido del AFD que se tiene que hacer para llegar a una cadena de entrada
def simulate_afd(afd, input_string):
    
        current_state = afd.start_state # Iniciar en el estado inicial del AFD

        # Para cada simbolo en la cadena de entrada
        for symbol in input_string:
             # Si hay una transicion definida para el simbolo actual
            if symbol in current_state.transitions:
                next_state = current_state.transitions[symbol]
                current_state = next_state # Mover al siguiente estado
            else:
                # Transicion no definida, la cadena no es aceptada
                return False

        # Devolver True si el estado final es alcanzado, de lo contrario False
        return current_state.is_final


# Minimizacion de un AFD dado utilizando el algoritmo de particiones (minimizacion de estados)
def minimize_afd(afd):

    # Inicializar particiones con estados finales y no finales
    partitions = [set(filter(lambda s: s.is_final, afd.states)),
                  set(filter(lambda s: not s.is_final, afd.states))]

    changed = True # Bandera para indicar si las particiones cambiaron
    
    while changed:
        changed = False         # Reiniciar la bandera
        new_partitions = []     # Lista para nuevas particiones
        
        # Para cada particion existente
        for partition in partitions:
            groups = {}  # Diccionario para agrupar estados equivalentes
            
            # Para cada estado en la particion
            for state in partition:
                key_elements = [] # Lista para elementos clave de transiciones
                
                # Para cada transicion del estado
                for symbol, next_state in state.transitions.items():
                    # Encontrar la particion a la que pertenece el estado siguiente
                    partition_index = next((i for i, p in enumerate(partitions) if next_state in p), -1)
                    key_elements.append((symbol, partition_index))
                key = tuple(sorted(key_elements)) # Crear una clave unica para el grupo


                # Agregar el estado al grupo correspondiente
                if key not in groups:
                    groups[key] = set()
                
                groups[key].add(state)
            
            # Si se crean multiples grupos, las particiones han cambiado
            if len(groups) > 1:
                changed = True
            
            # Agregar los nuevos grupos como nuevas particiones
            new_partitions.extend(groups.values())
            
        partitions = new_partitions # Actualizar las particiones

    # Crear un nuevo AFD minimizado
    minimized_afd = AFD()
    state_mapping = {}  # Diccionario para mapear estados antiguos a nuevos
    
    # Para cada particion, crear un nuevo estado en el AFD minimizado
    for partition in partitions:
        new_state = AFDState(set())
        new_state.is_final = any(state.is_final for state in partition)
        minimized_afd.add_state(new_state)

        # Mapear todos los estados antiguos en la particion al nuevo estado
        for old_state in partition:
            state_mapping[old_state] = new_state
    
    # Mapear las transiciones de los estados antiguos a los estados nuevos
    for old_state, new_state in state_mapping.items():
        for symbol, next_old_state in old_state.transitions.items():
            new_state.add_transition(symbol, state_mapping[next_old_state])
    
    # Establecer el estado inicial del AFD minimizado
    minimized_afd.start_state = state_mapping[afd.start_state]

    # Asignar numeros de estado a los estados en el AFD minimizado
    counter = len(minimized_afd.states)
    for state in minimized_afd.states:
        state.state_number = counter
        counter -= 1

    # Retornar el AFD minimizado
    return minimized_afd