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
    afd.start_state = initial_afd_state
    afd.add_state(initial_afd_state)

    unprocessed_states = [initial_afd_state]
    counter = 1

    while unprocessed_states:
        current_afd_state = unprocessed_states.pop()
        current_afd_state.state_number = counter
        counter += 1

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
                # Transición no definida, la cadena no es aceptada
                return False

        return current_state.is_final