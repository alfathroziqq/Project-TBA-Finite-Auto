from graphviz import Digraph

def visualize_dfa(dfa, filename):
    dot = Digraph(comment='DFA', format='png')
    dot.attr(rankdir='LR')

    # Tambahkan node
    for state in dfa['states']:
        if state in dfa['final_states']:
            dot.node(state, shape='doublecircle')
        else:
            dot.node(state)

    # Tambahkan transisi
    for start_state, transitions in dfa['transitions'].items():
        for symbol, next_state in transitions.items():
            dot.edge(start_state, next_state, label=symbol)

    dot.attr('node', shape='none', label='start')
    dot.node('')
    dot.edge('', dfa['initial_state'])

    dot.render(filename, cleanup=True)

def get_next_state(current_state, symbol, transitions):
    return transitions.get(current_state, {}).get(symbol)

def are_states_equivalent(state1, state2, dfa1, dfa2, equivalent_table):
    return equivalent_table[state1][state2]

def equivalent(dfa1, dfa2):
    def initialize_equivalence_table(dfa1, dfa2):
        equivalent_table = {}
        for state1 in dfa1['states']:
            equivalent_table[state1] = {}
            for state2 in dfa2['states']:
                equivalent_table[state1][state2] = (state1 in dfa1['final_states']) == (state2 in dfa2['final_states'])
        return equivalent_table

    # Initialize equivalence table
    equivalent_table = initialize_equivalence_table(dfa1, dfa2)

    # Check if any initial pair is not equivalent
    if not equivalent_table[dfa1['initial_state']][dfa2['initial_state']]:
        return False

    # Check for unreachable states and mark them as non-equivalent
    for state1 in dfa1['states']:
        for state2 in dfa2['states']:
            for symbol in dfa1['input_symbols']:
                next_state1 = get_next_state(state1, symbol, dfa1['transitions'])
                next_state2 = get_next_state(state2, symbol, dfa2['transitions'])
                if (next_state1 is None and next_state2 is not None) or (next_state1 is not None and next_state2 is None):
                    equivalent_table[state1][state2] = False

    # Iteratively refine equivalence table
    while True:
        changed = False
        for state1 in dfa1['states']:
            for state2 in dfa2['states']:
                if not equivalent_table[state1][state2]:
                    continue
                for symbol in dfa1['input_symbols']:
                    next_state1 = get_next_state(state1, symbol, dfa1['transitions'])
                    next_state2 = get_next_state(state2, symbol, dfa2['transitions'])
                    if not are_states_equivalent(next_state1, next_state2, dfa1, dfa2, equivalent_table):
                        equivalent_table[state1][state2] = False
                        changed = True
                        break
            if changed:
                break
        if not changed:
            break

    # Check if all states are equivalent
    for state1 in dfa1['states']:
        for state2 in dfa2['states']:
            if are_states_equivalent(state1, state2, dfa1, dfa2, equivalent_table):
                for symbol in dfa1['input_symbols']:
                    next_state1 = get_next_state(state1, symbol, dfa1['transitions'])
                    next_state2 = get_next_state(state2, symbol, dfa2['transitions'])
                    if not are_states_equivalent(next_state1, next_state2, dfa1, dfa2, equivalent_table):
                        return False
            else:
                if state1 in dfa1['final_states'] != state2 in dfa2['final_states']:
                    return False
    return True

dfa1 = {}
dfa1['states'] = input("Masukkan State DFA 1 (pisah dengan spasi): ").split()
dfa1['initial_state'] = input("Initial state: ")
dfa1['final_states'] = input("Final state (pisah dengan spasi bila > 1): ").split()
dfa1['input_symbols'] = input("Masukkan simbol input untuk DFA 1 (pisah dengan spasi): ").split()
dfa1['transitions'] = {}
for state in dfa1['states']:
    dfa1['transitions'][state] = {}
    for symbol in dfa1['input_symbols']:
        next_state = input(f"Transisi dari state {state} dengan simbol {symbol}: ")
        dfa1['transitions'][state][symbol] = next_state

dfa2 = {}
dfa2['states'] = input("Masukkan State DFA 2 (pisah dengan spasi): ").split()
dfa2['initial_state'] = input("Initial state: ")
dfa2['final_states'] = input("Final state (pisah dengan spasi bila > 1): ").split()
dfa2['input_symbols'] = input("Masukkan simbol input untuk DFA 2 (pisah dengan spasi): ").split()
dfa2['transitions'] = {}
for state in dfa2['states']:
    dfa2['transitions'][state] = {}
    for symbol in dfa2['input_symbols']:
        next_state = input(f"Transisi dari state {state} dengan simbol {symbol}: ")
        dfa2['transitions'][state][symbol] = next_state

# Pemanggilan fungsi visualize_dfa untuk menggambar grafik DFA
visualize_dfa(dfa1, "TBA\SC\\templates\DFA1")
visualize_dfa(dfa2, "TBA\SC\\templates\DFA2")

if equivalent(dfa1, dfa2):
    print("Kedua DFA Ekuivalen")
else:
    print("Kedua DFA Tidak Ekuivalen")