from graphviz import Digraph

def visualize_dfano3(dfa, filename):
    dot = Digraph(comment='DFA', format='png')
    dot.attr(rankdir='LR')

    # Tambahkan node
    for state in dfa.states:
        if state in dfa.final_states:
            dot.node(state, shape='doublecircle')
        else:
            dot.node(state)

    # Tambahkan transisi
    for start_state, transitions in dfa.transitions.items():
        for symbol, next_state in transitions.items():
            dot.edge(start_state, next_state, label=symbol)

    dot.attr('node', shape='none', label='start')
    dot.node('')
    dot.edge('', dfa.initial_state)

    dot.render(filename, cleanup=True)

class DFA:
    def __init__(self, states, input_symbols, transitions, initial_state, final_states):
        self.states = states
        self.input_symbols = input_symbols
        self.transitions = transitions
        self.initial_state = initial_state
        self.final_states = final_states

def get_next_state(current_state, symbol, transitions):
    return transitions.get(current_state, {}).get(symbol)

def are_states_equivalent(state1, state2, equivalence_classes):
    return equivalence_classes[state1][state2]

def remove_unreachable_states(automaton, start, visited=None):
    if visited is None:
        visited = set()
    visited.add(start)
    
    for neighbor in automaton.transitions[start]:
        if automaton.transitions[start][neighbor] not in visited:
            remove_unreachable_states(automaton, automaton.transitions[start][neighbor], visited)
    
    return list(sorted(visited))

def minimize_dfa(dfa):
    reachable_states = remove_unreachable_states(dfa, dfa.initial_state)
    
    equivalence_classes = {}
    for state1 in reachable_states:
        equivalence_classes[state1] = {}
        for state2 in reachable_states:
            equivalence_classes[state1][state2] = (state1 in dfa.final_states) == (state2 in dfa.final_states)

    for state1 in reachable_states:
        for state2 in reachable_states:
            for symbol in sorted(dfa.input_symbols):
                next_state1 = get_next_state(state1, symbol, dfa.transitions)
                next_state2 = get_next_state(state2, symbol, dfa.transitions)
                if (next_state1 is None and next_state2 is not None) or (next_state1 is not None and next_state2 is None):
                    equivalence_classes[state1][state2] = False

    while True:
        changed = False
        for state1 in reachable_states:
            for state2 in reachable_states:
                if not equivalence_classes[state1][state2]:
                    continue
                for symbol in sorted(dfa.input_symbols):
                    next_state1 = get_next_state(state1, symbol, dfa.transitions)
                    next_state2 = get_next_state(state2, symbol, dfa.transitions)
                    if not are_states_equivalent(next_state1, next_state2, equivalence_classes):
                        equivalence_classes[state1][state2] = False
                        changed = True
                        break
                if changed:
                    break
            if changed:
                break
        if not changed:
            break

    equivalence_group = {}
    group_counter = 0
    for state1 in reachable_states:
        if state1 not in equivalence_group.keys():
            group_counter += 1
            # equivalence_group[state1] = group_counter
            equivalence_group[state1] = state1
        for state2 in reachable_states:
            if state1 != state2 and equivalence_classes[state1][state2]:
                equivalence_group[state2] = equivalence_group[state1]

    new_states = {}
    for state in reachable_states:
        new_states[state] = str(equivalence_group[state])

    very_new_states = []
    new_final_state = []
    new_transition = []
    for state in reachable_states:
        very_new_states.append(new_states[state])
        if state in dfa.final_states:
            new_final_state.append(new_states[state])

    for state in reachable_states:
        for symbol in sorted(dfa.input_symbols):
            next_state = dfa.transitions[state].get(symbol)
            if next_state:
                next_state_new = new_states[next_state]
                transition = (new_states[state], symbol, next_state_new)
                new_transition.append(transition)

    converted_transitions = {}

    for transition in new_transition:
        start_state, symbol, next_state = transition
        if start_state not in converted_transitions:
            converted_transitions[start_state] = {}
        converted_transitions[start_state][symbol] = next_state

    new_dfa = DFA(
        states=very_new_states,
        input_symbols=sorted(dfa.input_symbols),
        transitions=converted_transitions,
        initial_state=str(new_states[dfa.initial_state]),
        final_states=new_final_state
    )

    return new_dfa

def create_dfa_from_input():
    states = input("Masukkan states (pisahkan dengan spasi): ").split()
    input_symbols = input("\nMasukkan input symbols (pisahkan dengan spasi): ").split()
    initial_state = input("\nMasukkan initial state: ")
    final_states = input("\nMasukkan final states (pisahkan dengan spasi): ").split()

    transitions = {}
    print("Masukkan transitions:")
    for state in states:
        transitions[state] = {}
        for symbol in input_symbols:
            next_state = input(f"Transisi dari state {state} dengan simbol {symbol}: ")
            transitions[state][symbol] = next_state

    dfa = DFA(
        states=set(states),
        input_symbols=input_symbols,
        transitions=transitions,
        initial_state=initial_state,
        final_states=set(final_states)
    )

    return dfa


def process_input_string(dfa, input_string):
    current_state = dfa.initial_state
    for symbol in input_string:
        next_state = get_next_state(current_state, symbol, dfa.transitions)
        if next_state is None:
            return False
        current_state = next_state
    return current_state in dfa.final_states


# Buat DFA dari input pengguna
user_dfa = create_dfa_from_input()

# Visualisasi DFA sebelum minimalisasi
visualize_dfano3(user_dfa, 'sebelum_min')

# Uji DFA sebelum minimalisasi
print("\nUJI DFA SEBELUM MINIMALISASI")
input_string = input("Masukkan string untuk diuji: ")

# Minimalisasi DFA
minimal_dfa = minimize_dfa(user_dfa)

# Visualisasi DFA setelah minimalisasi
visualize_dfano3(minimal_dfa, 'setelah_min')

# Uji DFA setelah minimalisasi
print("\nUJI DFA SETELAH MINIMALISASI")
input_string = input("Masukkan string untuk diuji: ")

# Output minimal DFA per baris
print("\nHASIL MINIMAL DFA")
print("States:")
print(", ".join(minimal_dfa.states))
print("\nInput Symbols:")
print(", ".join(minimal_dfa.input_symbols))
print("\nTransitions:")
for start_state, transitions in minimal_dfa.transitions.items():
    for symbol, next_state in transitions.items():
        print(f"{start_state} --({symbol})--> {next_state}")
print("\nInitial State:")
print(minimal_dfa.initial_state)
print("\nFinal States:")
print(", ".join(minimal_dfa.final_states))
print("\nString sebelum diminimalisasi:")
if process_input_string(user_dfa, input_string):
    print("DFA menerima string tersebut")
else:
    print("DFA tidak menerima string tersebut")
print("\nString setelah diminimalisasi:")
if process_input_string(minimal_dfa, input_string):
    print("DFA menerima string tersebut")
else:
    print("DFA tidak menerima string tersebut")