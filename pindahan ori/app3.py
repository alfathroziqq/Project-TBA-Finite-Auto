from flask import Flask, render_template, request
from graphviz import Digraph

app = Flask(__name__)

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

def state_to_string(state):
    if isinstance(state, str):
        return state
    else:
        return "".join(sorted(state))

def minimize_dfa(dfa):
    equivalence_classes = {}
    for state1 in sorted(dfa.states):
        equivalence_classes[state1] = {}
        for state2 in sorted(dfa.states):
            equivalence_classes[state1][state2] = (state1 in dfa.final_states) == (state2 in dfa.final_states)

    for state1 in sorted(dfa.states):
        for state2 in sorted(dfa.states):
            for symbol in sorted(dfa.input_symbols):
                next_state1 = get_next_state(state1, symbol, dfa.transitions)
                next_state2 = get_next_state(state2, symbol, dfa.transitions)
                if (next_state1 is None and next_state2 is not None) or (next_state1 is not None and next_state2 is None):
                    equivalence_classes[state1][state2] = False

    while True:
        changed = False
        for state1 in sorted(dfa.states):
            for state2 in sorted(dfa.states):
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
    for state1 in sorted(dfa.states):
        if state1 not in equivalence_group:
            group_counter += 1
            equivalence_group[state1] = group_counter
        for state2 in sorted(dfa.states):
            if state1 != state2 and equivalence_classes[state1][state2]:
                equivalence_group[state2] = equivalence_group[state1]

    new_states = {}
    for state in sorted(dfa.states):
        new_states[state] = "q" + str(equivalence_group[state])

    very_new_states = []
    new_final_state = []
    new_transition = []
    for state in sorted(dfa.states):
        very_new_states.append(new_states[state])
        if state in dfa.final_states:
            new_final_state.append(new_states[state])

    for state in sorted(dfa.states):
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

def process_input_string(dfa, input_string):
    current_state = dfa.initial_state
    for symbol in input_string:
        next_state = get_next_state(current_state, symbol, dfa.transitions)
        if next_state is None:
            return False
        current_state = next_state
    return current_state in dfa.final_states

def visualize_dfano3(dfa):
    dot = Digraph()
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

    return dot.pipe(format='svg').decode('utf-8')

@app.route('/')
def index():
    return render_template('index3.html')

@app.route('/submit3', methods=['POST'])
def submit():
    dfa = {}
    dfa['states'] = request.form['states'].split()
    dfa['input_symbols'] = request.form['inputSymbols'].split()
    dfa['initial_state'] = request.form['initialState']
    dfa['final_states'] = request.form['finalStates'].split()
    dfa['transitions'] = {}
    for state in dfa['states']:
        dfa['transitions'][state] = {}
        for symbol in dfa['input_symbols']:
            next_state = request.form.get(f'transitions_{state}_{symbol}')
            dfa['transitions'][state][symbol] = next_state

    # Buat DFA dari input pengguna
    user_dfa = DFA(
        states=set(dfa['states']),
        input_symbols=set(dfa['input_symbols']),
        transitions=dfa['transitions'],
        initial_state=dfa['initial_state'],
        final_states=set(dfa['final_states'])
    )

    # Uji DFA sebelum minimalisasi
    input_string = request.form['inputString']
    pre_minimization_result = "DFA menerima string yang diuji" if process_input_string(user_dfa, input_string) else "DFA tidak menerima string yang diuji"

    # Minimalisasi DFA
    minimal_dfa = minimize_dfa(user_dfa)

    # Uji DFA setelah minimalisasi
    post_minimization_result = "DFA menerima string yang diuji" if process_input_string(minimal_dfa, input_string) else "DFA tidak menerima string yang diuji"
    
    # Ambil nilai yang ingin ditampilkan
    state_result = ", ".join(minimal_dfa.states)
    symbol_result = ", ".join(minimal_dfa.input_symbols)
    transition_result = []
    for start_state, transitions in minimal_dfa.transitions.items():
        for symbol, next_state in transitions.items():
            transition_result.append([start_state, symbol, next_state])
    initial_result = minimal_dfa.initial_state
    final_result = ", ".join(minimal_dfa.final_states)
    
    graph_dfano3 = visualize_dfano3(user_dfa)
    graph_minimized_dfano3 = visualize_dfano3(minimal_dfa)

    return render_template('index3.html', state_result=state_result, symbol_result=symbol_result, 
                           transition_result=transition_result, initial_result=initial_result, 
                           final_result=final_result, pre_minimization_result=pre_minimization_result,
                           post_minimization_result=post_minimization_result, graph_dfano3=graph_dfano3, graph_minimized_dfano3=graph_minimized_dfano3)


if __name__ == "__main__":
    app.run(debug=True)
