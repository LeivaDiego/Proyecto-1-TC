from graphviz import Digraph


class AFD:
    def __init__(self):
        self.states = []
        self.start_state = None
        self.end_states = []

    def add_state(self, state):
        self.states.append(state)
        if state.is_final:
            self.end_states.append(state)

    def visualize_afd(self):
            dot = Digraph()
            for state in self.states:
                if state == self.start_state:
                    dot.node(str(id(state)), label=f"{state.state_number}", shape="ellipse")
                elif state.is_final:
                    dot.node(str(id(state)), label=f"{state.state_number}", shape="doublecircle")
                else:
                    dot.node(str(id(state)), label=str(state.state_number), shape="ellipse")

                for symbol, next_state in state.transitions.items():
                    dot.edge(str(id(state)), str(id(next_state)), label=symbol)

            return dot


class AFDState:
    def __init__(self, afn_states):
        self.afn_states = afn_states
        self.transitions = {}
        self.is_final = any(state.is_final for state in afn_states)
        self.state_number = None

    def add_transition(self, symbol, state):
        self.transitions[symbol] = state


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



def convert_to_afd(afn):
    afd = AFD()
    initial_afn_states = epsilon_closure(set([afn.start_state]))
    initial_afd_state = AFDState(initial_afn_states)
    initial_afd_state.state_number = 1
    afd.start_state = initial_afd_state
    afd.add_state(initial_afd_state)

    unprocessed_states = [initial_afd_state]
    counter = 2  

    while unprocessed_states:
        current_afd_state = unprocessed_states.pop()

        symbols = set()
        for afn_state in current_afd_state.afn_states:
            symbols.update(afn_state.transitions.keys())

        if None in symbols:
            symbols.remove(None)

        for symbol in symbols:
            new_afn_states = set()
            for afn_state in current_afd_state.afn_states:
                if symbol in afn_state.transitions:
                    new_afn_states.update(afn_state.transitions[symbol])

            new_afn_states = epsilon_closure(new_afn_states)
            existing_state = next((state for state in afd.states if state.afn_states == new_afn_states), None)

            if existing_state is None:
                new_afd_state = AFDState(new_afn_states)
                new_afd_state.state_number = counter 
                counter += 1
                afd.add_state(new_afd_state)
                unprocessed_states.append(new_afd_state)
                current_afd_state.add_transition(symbol, new_afd_state)
            else:
                current_afd_state.add_transition(symbol, existing_state)

    return afd

def simulate_afd(afd, input_string):
        current_state = afd.start_state

        for symbol in input_string:
            if symbol in current_state.transitions:
                next_state = current_state.transitions[symbol]
                current_state = next_state
            else:
                # Transicion no definida, la cadena no es aceptada
                return False

        return current_state.is_final


def minimize_afd(afd):
    partitions = [set(filter(lambda s: s.is_final, afd.states)),
                  set(filter(lambda s: not s.is_final, afd.states))]
    
    state_number = 1
    
    changed = True
    while changed:
        changed = False
        new_partitions = []
        
        for partition in partitions:
            groups = {}
            
            for state in partition:
                key = tuple(sorted((symbol, next_state.state_number) for symbol, next_state in state.transitions.items()))
                
                if key not in groups:
                    groups[key] = set()
                
                groups[key].add(state)
                
            if len(groups) > 1:
                changed = True
            
            new_partitions.extend(groups.values())
            
        partitions = new_partitions
    
    minimized_afd = AFD()
    state_mapping = {}
    
    for partition in partitions:
        new_state = AFDState(set())
        new_state.is_final = any(state.is_final for state in partition)
        new_state.state_number = state_number
        state_number += 1
        minimized_afd.add_state(new_state)
        
        for old_state in partition:
            state_mapping[old_state] = new_state
    
    for old_state, new_state in state_mapping.items():
        for symbol, next_old_state in old_state.transitions.items():
            new_state.add_transition(symbol, state_mapping[next_old_state])
    
    minimized_afd.start_state = state_mapping[afd.start_state]
    
    return minimized_afd
